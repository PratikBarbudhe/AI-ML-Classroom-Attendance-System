"""
Attendance tracking and storage module.
Manages SQLite database for marking and exporting attendance records.
Includes deduplication logic and thread-safe operations.
"""

import csv
import os
import sqlite3
import threading
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class AttendanceStore:
    def __init__(self, db_path=None):
        """
        Initialize attendance store.
        
        Args:
            db_path: Path to SQLite database (uses config default if None)
        """
        if db_path is None:
            db_path = str(config.ATTENDANCE_DB)
        
        self.db_path = db_path
        self._lock = threading.Lock()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        logger.info(f"Initializing AttendanceStore with database: {self.db_path}")
        self._init_db()

    def _connect(self):
        """
        Create a database connection with proper error handling.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        try:
            return sqlite3.connect(self.db_path, check_same_thread=False)
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def _init_db(self):
        """
        Initialize the database schema.
        Creates attendance table if it doesn't exist.
        """
        with self._lock:
            conn = None
            try:
                conn = self._connect()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        person_name TEXT NOT NULL,
                        recognized_at TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        source TEXT NOT NULL
                    )
                    """
                )
                
                # Create index for faster queries
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_person_time 
                    ON attendance(person_name, recognized_at)
                    """
                )
                
                conn.commit()
                logger.info("Database initialized successfully")
            except sqlite3.Error as e:
                logger.error(f"Database initialization error: {e}")
                raise
            finally:
                if conn:
                    conn.close()

    def mark_attendance(self, person_name, confidence, source=None, min_interval_seconds=None):
        """
        Mark attendance for a person with deduplication.
        
        Args:
            person_name: Name of the person
            confidence: Confidence score of recognition (0-1 normalized, or raw LBPH distance 0-100)
            source: Source of attendance (uses config default if None)
            min_interval_seconds: Minimum seconds between marking (uses config default if None)
        
        Returns:
            tuple: (success, message)
        """
        if source is None:
            source = config.ATTENDANCE_SOURCE
        
        if min_interval_seconds is None:
            min_interval_seconds = config.ATTENDANCE_MIN_INTERVAL
        
        # Validate inputs
        if not isinstance(person_name, str) or not person_name.strip():
            logger.warning("Invalid person name provided to mark_attendance")
            return False, "Invalid person name"
        
        try:
            confidence = float(confidence)
            
            # ✅ PROPER LBPH CONFIDENCE NORMALIZATION
            if confidence > 1:
                # Raw LBPH distance score (typically 0-100)
                # LBPH returns distance where LOWER is better
                # Convert to confidence where HIGHER is better
                original_distance = confidence
                lbph_max_distance = config.LBPH_MAX_DISTANCE
                confidence = max(0, min(1, 1 - (confidence / lbph_max_distance)))
                logger.debug(f"Converted LBPH distance {original_distance:.2f} to normalized confidence: {confidence:.2%}")
            elif confidence < 0:
                # Negative values - clip to 0
                confidence = 0
                logger.warning(f"Negative confidence value clipped to 0")
            # else: confidence is already in 0-1 range, keep as is
            
        except (ValueError, TypeError):
            logger.warning(f"Invalid confidence value: {confidence}")
            return False, "Invalid confidence value"
        
        now = datetime.now()
        now_iso = now.strftime("%Y-%m-%d %H:%M:%S")
        
        with self._lock:
            conn = None
            try:
                conn = self._connect()
                cursor = conn.cursor()
                
                # Check for duplicate attendance within time window
                cursor.execute(
                    """
                    SELECT recognized_at FROM attendance
                    WHERE person_name = ?
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (person_name,),
                )
                row = cursor.fetchone()
                
                if row:
                    last_seen = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                    delta = (now - last_seen).total_seconds()
                    if delta < min_interval_seconds:
                        return False, f"Duplicate attendance skipped for {person_name}"
                
                # Insert new attendance record
                cursor.execute(
                    """
                    INSERT INTO attendance (person_name, recognized_at, confidence, source)
                    VALUES (?, ?, ?, ?)
                    """,
                    (person_name, now_iso, confidence, source),
                )
                conn.commit()
                logger.info(f"Attendance marked for {person_name} (confidence: {confidence:.2%})")
                return True, f"Attendance marked for {person_name}"
            
            except sqlite3.Error as e:
                logger.error(f"Error marking attendance: {e}")
                return False, f"Database error: {str(e)}"
            
            finally:
                if conn:
                    conn.close()

    def get_today_records(self):
        """
        Get all attendance records for today.
        
        Returns:
            list: List of attendance record dictionaries
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        with self._lock:
            conn = None
            try:
                conn = self._connect()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT person_name, recognized_at, confidence, source
                    FROM attendance
                    WHERE recognized_at LIKE ?
                    ORDER BY recognized_at DESC
                    """,
                    (f"{today}%",),
                )
                rows = cursor.fetchall()
                
                records = [
                    {
                        "person_name": row[0],
                        "recognized_at": row[1],
                        "confidence": row[2],
                        "source": row[3],
                    }
                    for row in rows
                ]
                
                logger.info(f"Retrieved {len(records)} records for today")
                return records
            
            except sqlite3.Error as e:
                logger.error(f"Error retrieving today's records: {e}")
                return []
            
            finally:
                if conn:
                    conn.close()


    def get_today_summary(self):
        """
        Get summary statistics for today's attendance.
        
        Returns:
            dict: Statistics including total events, unique people, last event
        """
        records = self.get_today_records()
        
        if not records:
            return {
                "total_events": 0,
                "unique_people": 0,
                "last_event": None,
            }
        
        unique_people = len({item["person_name"] for item in records})
        
        return {
            "total_events": len(records),
            "unique_people": unique_people,
            "last_event": records[0] if records else None,
        }

    def export_today_csv(self, output_path=None):
        """
        Export today's attendance records to CSV.
        
        Args:
            output_path: Output CSV file path (generates default if None)
        
        Returns:
            tuple: (output_path, record_count) or (None, 0) on error
        """
        records = self.get_today_records()
        
        if not records:
            logger.warning("No records to export")
            return None, 0
        
        try:
            if output_path is None:
                os.makedirs(str(config.EXPORTS_DIR), exist_ok=True)
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(config.EXPORTS_DIR / f"attendance_{stamp}.csv")
            
            with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=["person_name", "recognized_at", "confidence", "source"],
                )
                writer.writeheader()
                for row in records:
                    writer.writerow(row)
            
            logger.info(f"Exported {len(records)} records to {output_path}")
            return output_path, len(records)
        
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return None, 0
