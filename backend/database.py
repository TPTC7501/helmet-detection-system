"""SQLite database models and operations."""

import sqlite3
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: str = 'helmet_detection.db'):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def init_database(self):
        """Initialize database schema."""
        self.connect()
        
        # Create events table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                frame_number INTEGER,
                track_id INTEGER,
                detection_type VARCHAR(20),
                confidence REAL,
                bbox_x1 REAL,
                bbox_y1 REAL,
                bbox_x2 REAL,
                bbox_y2 REAL,
                evidence_image_path VARCHAR(255),
                camera_source VARCHAR(255)
            )
        ''')
        
        # Create statistics table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_frames INTEGER,
                total_unique_persons INTEGER,
                helmet_count INTEGER,
                no_helmet_count INTEGER,
                false_positive_rate REAL,
                avg_confidence REAL,
                processing_time_ms REAL
            )
        ''')
        
        # Create indexes
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_track_id ON events(track_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_detection_type ON events(detection_type)')
        
        self.conn.commit()
        logger.info(f"Database initialized: {self.db_path}")
    
    def connect(self):
        """Connect to database."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.debug(f"Connected to database: {self.db_path}")
    
    def insert_event(self, event) -> int:
        """Insert event into database."""
        self.cursor.execute('''
            INSERT INTO events 
            (frame_number, track_id, detection_type, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2, evidence_image_path, camera_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.frame_number,
            event.track_id,
            event.detection_type,
            event.confidence,
            event.bbox[0],
            event.bbox[1],
            event.bbox[2],
            event.bbox[3],
            event.evidence_image_path,
            event.camera_source
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_events(self, start_time: datetime = None, end_time: datetime = None, detection_type: str = None) -> list:
        """Get events within time range."""
        query = 'SELECT * FROM events WHERE 1=1'
        params = []
        
        if start_time:
            query += ' AND timestamp >= ?'
            params.append(start_time.isoformat())
        
        if end_time:
            query += ' AND timestamp <= ?'
            params.append(end_time.isoformat())
        
        if detection_type:
            query += ' AND detection_type = ?'
            params.append(detection_type)
        
        query += ' ORDER BY timestamp DESC'
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def get_event_count(self, detection_type: str = None) -> int:
        """Get total event count."""
        query = 'SELECT COUNT(*) as count FROM events WHERE 1=1'
        params = []
        
        if detection_type:
            query += ' AND detection_type = ?'
            params.append(detection_type)
        
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()
        return result['count'] if result else 0
    
    def insert_statistics(self, stats: dict) -> int:
        """Insert statistics record."""
        self.cursor.execute('''
            INSERT INTO statistics 
            (total_frames, total_unique_persons, helmet_count, no_helmet_count, false_positive_rate, avg_confidence, processing_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            stats.get('total_frames', 0),
            stats.get('total_unique_persons', 0),
            stats.get('helmet_count', 0),
            stats.get('no_helmet_count', 0),
            stats.get('false_positive_rate', 0),
            stats.get('avg_confidence', 0),
            stats.get('processing_time_ms', 0)
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_statistics(self, limit: int = 100) -> list:
        """Get recent statistics."""
        self.cursor.execute('SELECT * FROM statistics ORDER BY session_start DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.debug("Database connection closed")
    
    def cleanup_old_events(self, days: int = 30):
        """Remove events older than specified days."""
        self.cursor.execute('''
            DELETE FROM events WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')
        ''', (days,))
        deleted = self.cursor.rowcount
        self.conn.commit()
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} events older than {days} days")
        return deleted
