import logging
import sqlite3

from contextlib import contextmanager
from typing import Iterator, Optional
from threading import Lock
from src.config.settings import DATABASE_PATH

# setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

_CONNECTION_LOCK = Lock()  # lock for thread-safe connection management

@contextmanager
def get_db_connection(
    db_path: str = DATABASE_PATH,
    timeout: float = 5.0,
    detect_types: int = sqlite3.PARSE_DECLTYPES,
    isolation_level: Optional[str] = None ) -> Iterator[sqlite3.Connection]:
    """
    SQLite database connection context manager
    """
    conn = None
    try:
        with _CONNECTION_LOCK:
            conn = sqlite3.connect(
                db_path,
                timeout=timeout,
                detect_types=detect_types,
                isolation_level=isolation_level
            )
            logging.info(f"Connected to SQLite database at {db_path}")
            # Enable foreign keys and WAL mode
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON") # make sure foreign keys are enabled
            conn.execute("PRAGMA journal_mode = WAL") 
            conn.execute("PRAGMA busy_timeout = 5000")  # 5 seconds timeout
            
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -20000")  # 20MB cache
        yield conn

    except sqlite3.Error as error:
        logging.error(
            f"Database connection failed (path={db_path}): {str(error)}",
            exc_info=True
        )
        raise sqlite3.DatabaseError(f"Connection failed: {error}") from error
    finally:
        if conn:
            try:
                conn.close()
            except sqlite3.Error as e:
                logging.warning(f"Connection close failed: {e}")

def initialize_database():
    """intialize database tables"""
    with get_db_connection() as conn:
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT,
                    result TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    timestamp DATETIME,
                    data TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                )
            ''')
            conn.commit()
        except sqlite3.Error as error:
            logging.error(f"Error creating tables: {error}")
            raise sqlite3.DatabaseError(f"Creating tables failed: {error}") from error