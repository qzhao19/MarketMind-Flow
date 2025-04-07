import unittest
from unittest.mock import MagicMock, patch
import sqlite3
import tempfile
import os

from contextlib import contextmanager
from datetime import datetime
from typing import List
from src.core.job_management.job_schemas import Job, Event
from src.services.database.connection import get_db_connection, initialize_database
from src.services.database.job_store import append_event, update_job_by_id, get_job_by_id


class TestJobFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """create temp database environment"""
        # 1. create temp db filepath
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.db_path = cls.temp_db.name
        
        # 2. backup and modify DATABASE_PATH
        from src.services.database.connection import DATABASE_PATH
        cls.original_db_path = DATABASE_PATH
        DATABASE_PATH = cls.db_path
        
        # 3. initialize database with PRAGMA to defer foreign key checks
        with get_db_connection() as conn:
            conn.execute("PRAGMA foreign_keys = OFF")  # Temporarily disable
            initialize_database()
            conn.execute("PRAGMA foreign_keys = ON")   # Re-enable
            conn.commit()

    @classmethod
    def tearDownClass(cls):
        """cleanup test environment"""
        from src.services.database.connection import DATABASE_PATH
        # 1. restore DATABASE_PATH
        DATABASE_PATH = cls.original_db_path
        # 2. remove temp db file
        os.unlink(cls.db_path)

    def setUp(self):
        """cleanup data before testing"""
        with get_db_connection() as conn:
            # Must delete in correct order due to foreign key constraints
            conn.execute("DELETE FROM events")  # Child table first
            conn.execute("DELETE FROM jobs")   # Parent table last
            conn.commit()

    def test_append_event_new_job(self):
        """recording new job event"""
        # execute test
        append_event("test_job_1", "test_event_data")
        
        # check jobs table
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM jobs WHERE job_id = ?", ("test_job_1",))
            job = cursor.fetchone()
            self.assertIsNotNone(job)
            self.assertEqual(job[0], "STARTED")
        
        # check events table
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM events WHERE job_id = ?", ("test_job_1",))
            event = cursor.fetchone()
            self.assertIsNotNone(event)
            self.assertEqual(event[0], "test_event_data")

    def test_update_job_by_id(self):
        """update job status and result"""
        # create a job and its event together in a transaction
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO jobs (job_id, status, result) 
                VALUES (?, ?, ?)
            """, ("test_job_3", "STARTED", ""))
            
            conn.execute("""
                INSERT INTO events (job_id, timestamp, data) 
                VALUES (?, ?, ?)
            """, ("test_job_3", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "initial_event"))
            conn.commit()

        # execute test
        update_job_by_id("test_job_3", "COMPLETED", "test_result", ["test_event_data"])
        
        # check jobs table
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, result FROM jobs WHERE job_id = ?
            """, ("test_job_3",))
            job = cursor.fetchone()
            self.assertIsNotNone(job)
            self.assertEqual(job[0], "COMPLETED")
            self.assertEqual(job[1], "test_result")
        
        # check events table
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data FROM events 
                WHERE job_id = ? ORDER BY timestamp DESC
            """, ("test_job_3",))
            events = cursor.fetchall()
            self.assertEqual(len(events), 2)  # initial + new event
            self.assertEqual(events[1][0], "test_event_data")  # newest first

    def test_get_job_by_id(self):
        """retrieve job details by job_id"""
        # create a job and its event together in a transaction
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO jobs (job_id, status, result)
                VALUES (?,?,?)
            """, ("test_job_4", "STARTED", ""))

            conn.execute("""
                INSERT INTO events (job_id, timestamp, data)
                VALUES (?,?,?)
            """, ("test_job_4", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "initial_event"))
            conn.commit()
        # execute test
        job = get_job_by_id("test_job_4")
        self.assertIsNotNone(job)
        self.assertEqual(job.result, "")
        self.assertEqual(job.status, "STARTED")
        self.assertEqual(len(job.events), 1)
        # print(job.events[0].data)
        self.assertEqual(job.events[0].data, "initial_event")

