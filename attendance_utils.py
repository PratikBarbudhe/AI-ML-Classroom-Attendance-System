import csv
import os
import sqlite3
import threading
from datetime import datetime


class AttendanceStore:
    def __init__(self, db_path="data/attendance/attendance.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        with self._lock:
            conn = self._connect()
            try:
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
                conn.commit()
            finally:
                conn.close()

    def mark_attendance(self, person_name, confidence, source="webcam", min_interval_seconds=60):
        now = datetime.now()
        now_iso = now.strftime("%Y-%m-%d %H:%M:%S")

        with self._lock:
            conn = self._connect()
            try:
                cursor = conn.cursor()
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
                        return False, f"Skipped duplicate for {person_name}"

                cursor.execute(
                    """
                    INSERT INTO attendance (person_name, recognized_at, confidence, source)
                    VALUES (?, ?, ?, ?)
                    """,
                    (person_name, now_iso, float(confidence), source),
                )
                conn.commit()
                return True, f"Attendance marked for {person_name}"
            finally:
                conn.close()

    def get_today_records(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with self._lock:
            conn = self._connect()
            try:
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
                return [
                    {
                        "person_name": row[0],
                        "recognized_at": row[1],
                        "confidence": row[2],
                        "source": row[3],
                    }
                    for row in rows
                ]
            finally:
                conn.close()

    def get_today_summary(self):
        records = self.get_today_records()
        unique_people = len({item["person_name"] for item in records})
        return {
            "total_events": len(records),
            "unique_people": unique_people,
            "last_event": records[0] if records else None,
        }

    def export_today_csv(self, output_path=None):
        records = self.get_today_records()
        if output_path is None:
            export_dir = "data/attendance/exports"
            os.makedirs(export_dir, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(export_dir, f"attendance_{stamp}.csv")

        with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=["person_name", "recognized_at", "confidence", "source"],
            )
            writer.writeheader()
            for row in records:
                writer.writerow(row)

        return output_path, len(records)
