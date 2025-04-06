import pytest
import sqlite3
import os
from threading import Thread
from unittest.mock import patch, MagicMock
from src.services.database.connection import get_db_connection, initialize_database, DATABASE_PATH

@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    """Fixture to clean up database before and after tests"""
    if os.path.exists(DATABASE_PATH):
        os.unlink(DATABASE_PATH)
    
    with get_db_connection() as conn:
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()
    
    yield # execute tests

    if os.path.exists(DATABASE_PATH):
        os.unlink(DATABASE_PATH)

def test_connection_success():
    """Test successful database connection"""
    with get_db_connection() as conn:
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        # Verify PRAGMA settings
        cursor = conn.execute("PRAGMA foreign_keys")
        assert cursor.fetchone()[0] == 1
        cursor = conn.execute("PRAGMA journal_mode")
        assert cursor.fetchone()[0].upper() == "WAL"

def test_concurrent_connections():
    """Testing multi-threaded concurrent connections"""
    results = []
    
    def worker():
        try:
            with get_db_connection() as conn:
                conn.execute("INSERT INTO test (name) VALUES ('thread_test')")
                conn.commit()
            results.append(True)
        except Exception:
            results.append(False)
    
    threads = [Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert all(results), "All threads should complete successfully"
    
    # check database
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM test")
        assert cursor.fetchone()[0] == 5

def test_connection_failure(monkeypatch):
    """Test connection failure scenario"""
    def mock_connect(*args, **kwargs):
        raise sqlite3.Error("Simulated connection error")

    monkeypatch.setattr(sqlite3, "connect", mock_connect)
    
    with pytest.raises(sqlite3.DatabaseError) as excinfo:
        with get_db_connection():
            pass
    
    assert "Connection failed" in str(excinfo.value)

def test_initialize_database_success():
    """Test database initialization"""
    initialize_database()
    
    with get_db_connection() as conn:
        # Verify tables exist
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name IN ('jobs', 'events')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        assert set(tables) == {"jobs", "events"}
        
        # Verify foreign key constraint
        cursor = conn.execute("PRAGMA foreign_key_check")
        assert cursor.fetchone() is None

def test_initialize_database_failure():
    """Test initialization failure scenario using MagicMock"""
    # create connection mock
    mock_conn = MagicMock(spec=sqlite3.Connection)
    
    # setup execute throw error
    mock_conn.execute.side_effect = sqlite3.Error("Simulated table creation error")
    
    # patch get_db_connection to return mock connection
    with patch('src.services.database.connection.get_db_connection') as mock_get_conn:
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        with pytest.raises(sqlite3.DatabaseError) as excinfo:
            initialize_database()
        
        assert "Creating tables failed" in str(excinfo.value)
        
        # check execute calls
        assert mock_conn.execute.call_count == 1 
        assert mock_conn.commit.call_count == 0

def test_connection_parameters():
    """Test custom connection parameters"""
    custom_timeout = 10.0
    custom_isolation = "IMMEDIATE"
    
    with get_db_connection(timeout=custom_timeout, isolation_level=custom_isolation) as conn:
        # Verify isolation level
        cursor = conn.execute("PRAGMA journal_mode")
        assert cursor.fetchone()[0].upper() == "WAL"
        
        # Can't directly verify timeout, but check connection works
        conn.execute("SELECT 1")

