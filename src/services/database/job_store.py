import logging
import sqlite3

from datetime import datetime
from typing import List
from threading import Lock
from src.core.job_management.job_schemas import Event, Job
from .connection import get_db_connection

_logger = logging.getLogger(__name__)
_op_lock = Lock()

def record_event(job_id: str, event_data: str):
    """record event"""
    try:
        with _op_lock, get_db_connection() as conn:
            if not conn:
                logging.error("Database connection failed")
                return None
            
            cursor = conn.cursor()
            # check if job exists
            cursor.execute(
                "SELECT job_id FROM jobs WHERE job_id = ?", (job_id,)
            )
            job_exists  = cursor.fetchone() is not None

            # if job does not exist, create a new job
            if not job_exists:
                conn.execute(
                    """INSERT INTO jobs (job_id, status, result)
                    VALUES (?, 'STARTED', '')
                    ON CONFLICT(job_id) DO NOTHING""",
                    (job_id,)
                )
                logging.info(f"Job {job_id} started")
            else:
                logging.info(f"Recording event for job {job_id}: {event_data}")
            
            # create a new event record
            # timestamp format: yyyy-MM-dd HH:mm:ss
            conn.execute(
                """INSERT INTO events (job_id, timestamp, data) VALUES (?, ?, ?)""",
                (job_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), event_data)
            )
            conn.commit()
            logging.info(f"Event recorded for job {job_id}")

    except sqlite3.IntegrityError as e:
        logging.warning(f"Integrity violation: {e}", exc_info=True)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}", exc_info=True)
    except Exception as e:
        logging.critical(f"Unexpected error: {e}", exc_info=True)
        raise


def update_job_by_id(job_id: str, status: str, result: str, event_data: List[str]) -> bool:
    """
    Update job status and result, and append events in a single transaction.
    Returns True if successful, False otherwise.
    """
    try:
        with _op_lock, get_db_connection() as conn:
            if not conn:
                logging.error("Database connection failed")
                return None
            
            cursor = conn.cursor()
            # Check if job exists (more efficient than SELECT *)
            cursor.execute("SELECT 1 FROM jobs WHERE job_id =? LIMIT 1", (job_id,))

            if not cursor.fetchone():
                logging.warning(f"Job {job_id} not found")
                return False
            # Update job (using RETURNING in SQLite 3.35+ for verification)
            cursor.execute(
                "UPDATE jobs SET status =?, result =? WHERE job_id =?",
                (status, result, job_id)
            )
            if cursor.rowcount == 0:  # Verify update occurred
                logging.warning(f"No rows updated for job {job_id}")
                return False
            
            # Batch insert events (more efficient than individual inserts)
            if event_data:
                try:
                    cursor.executemany(
                        "INSERT INTO events (job_id, timestamp, data) VALUES (?, ?, ?)",
                        [(job_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), event) for event in event_data]
                    )
                except sqlite3.IntegrityError:
                    logging.error(f"Invalid job_id {job_id} when inserting events")
                    conn.rollback()
                    return False
            conn.commit()
            logging.info(f"Updated job {job_id} with {len(event_data)} events")
            return True

    except sqlite3.Error as e:
        logging.error(f"Database error updating job {job_id}: {str(e)}")
        return False
            
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return False


def get_job_by_id(job_id: str) -> Job:
    """
    Retrieve job details by job_id.
    Returns Job object if found, None otherwise.
    """
    try:
        with _op_lock, get_db_connection() as conn:
            if not conn:
                logging.error("Database connection failed")
                return None

            cursor = conn.cursor()
            cursor.execute(
                """SELECT job_id, status, result FROM jobs WHERE job_id =?""",
                (job_id,)
            )
            job_data = cursor.fetchone()
            if not job_data:
                logging.warning(f"Job {job_id} not found")
                return None
            
            # from events table to select data, timestamp
            cursor.execute(
                """SELECT data, timestamp FROM events WHERE job_id =?""",
                (job_id,)
            )
            event_data = cursor.fetchall()

            # convert to Job object
            if not event_data:
                logging.warning(f"No events found for job {job_id}")
                return Job(status=job_data[1], events=[], result=job_data[2])
            
            # create job object and return
            events = [Event(timestamp=row[1], data=row[0]) for row in event_data]
            job = Job(status=job_data[1], events = events, result = job_data[2])
            return job
    
    except sqlite3.Error as e:
        logging.error(f"Database error retrieving job {job_id}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return None



