"""
Database Manager for Kids Educational Content Automation
Handles topic storage, usage tracking, and upload history
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


class DBManager:
    def __init__(self, db_path="app_data.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Topics table with enhanced structure
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    main_topic TEXT NOT NULL,
                    subtopic TEXT NOT NULL,
                    status TEXT DEFAULT 'unused',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_at TIMESTAMP NULL,
                    UNIQUE(category, main_topic, subtopic)
                )
            """)
            
            # Upload history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS upload_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER,
                    video_title TEXT,
                    youtube_video_id TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (topic_id) REFERENCES topics (id)
                )
            """)
            
            # Logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()

    def add_topics(self, topics_list: List[Dict]) -> int:
        """
        Add multiple topics to database
        
        Args:
            topics_list: List of topic dictionaries with keys: category, main_topic, subtopic
            
        Returns:
            Number of topics successfully added
        """
        added_count = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for topic in topics_list:
                try:
                    cursor.execute(
                        "INSERT INTO topics (category, main_topic, subtopic, status) VALUES (?, ?, ?, ?)",
                        (topic['category'], topic['main_topic'], topic['subtopic'], 'unused')
                    )
                    added_count += 1
                except sqlite3.IntegrityError:
                    # Skip duplicate topics
                    continue
            conn.commit()
        return added_count

    def get_next_topic(self) -> Optional[Dict]:
        """
        Get the next unused topic
        
        Returns:
            Dictionary with topic data or None if no topics available
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, main_topic, subtopic 
                FROM topics 
                WHERE status = 'unused' 
                ORDER BY id 
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "category": row[1],
                    "main_topic": row[2],
                    "subtopic": row[3]
                }
            return None

    def mark_topic_used(self, topic_id: int):
        """Mark a topic as used"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE topics SET status = 'used', used_at = ? WHERE id = ?",
                (datetime.now(), topic_id)
            )
            conn.commit()

    def get_unused_count(self) -> int:
        """Get count of unused topics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM topics WHERE status = 'unused'")
            return cursor.fetchone()[0]

    def get_total_count(self) -> int:
        """Get total count of all topics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM topics")
            return cursor.fetchone()[0]

    def reset_all_topics(self):
        """Reset all topics to unused status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE topics SET status = 'unused', used_at = NULL")
            conn.commit()

    def delete_all_topics(self):
        """Delete all topics from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM topics")
            conn.commit()

    def log_upload(self, topic_id: int, video_title: str, youtube_video_id: str):
        """Log successful video upload"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO upload_history (topic_id, video_title, youtube_video_id) VALUES (?, ?, ?)",
                (topic_id, video_title, youtube_video_id)
            )
            conn.commit()

    def add_log(self, level: str, message: str):
        """Add a log entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs (level, message) VALUES (?, ?)",
                (level, message)
            )
            conn.commit()

    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent log entries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT level, message, created_at FROM logs ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                {"level": row[0], "message": row[1], "created_at": row[2]}
                for row in rows
            ]

    def cleanup_old_logs(self, days: int = 30):
        """Delete logs older than specified days"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM logs WHERE created_at < datetime('now', '-' || ? || ' days')",
                (days,)
            )
            conn.commit()
