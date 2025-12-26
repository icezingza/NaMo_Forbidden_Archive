"""
Memory service with SQLite backend instead of JSON.
"""

import sqlite3
import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class MemoryServiceDB:
    """
    SQLite-based memory service with better performance.
    """

    def __init__(self, db_path: str = "memories.db"):
        """
        Initialize memory service with database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.lock = threading.RLock()
        self.logger = logging.getLogger(f"{__name__}.MemoryServiceDB")

        # Create database and tables
        self._init_db()

    @contextmanager
    def get_db_connection(self):
        """
        Context manager for database connection.

        Yields:
            SQLite connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            # Create memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    type TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    emotion_json TEXT,
                    tags_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON memories(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created ON memories(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON memories(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_content ON memories(content)")

            # Create tags table for better search
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_tags (
                    memory_id TEXT,
                    tag TEXT,
                    FOREIGN KEY(memory_id) REFERENCES memories(id),
                    PRIMARY KEY(memory_id, tag)
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag ON memory_tags(tag)")

            # Create statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS access_stats (
                    memory_id TEXT PRIMARY KEY,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    FOREIGN KEY(memory_id) REFERENCES memories(id)
                )
            """)

            conn.commit()
            self.logger.info("Database initialized successfully")

    def store_memory(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store memory in database.

        Args:
            memory_data: Memory data to store

        Returns:
            Stored memory with ID and timestamp
        """
        with self.lock:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                memory_id = memory_data.get("id") or f"mem_{int(datetime.now().timestamp())}"
                content = memory_data["content"]
                mem_type = memory_data["type"]
                session_id = memory_data["session_id"]
                emotion_context = memory_data.get("emotion_context")
                dharma_tags = memory_data.get("dharma_tags", [])

                # Insert memory
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO memories 
                    (id, content, type, session_id, emotion_json, tags_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        memory_id,
                        content,
                        mem_type,
                        session_id,
                        json.dumps(emotion_context) if emotion_context else None,
                        json.dumps(dharma_tags) if dharma_tags else None,
                        datetime.now().isoformat(),
                    ),
                )

                # Insert tags
                for tag in dharma_tags:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO memory_tags (memory_id, tag)
                        VALUES (?, ?)
                    """,
                        (memory_id, tag),
                    )

                # Initialize stats
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO access_stats (memory_id, access_count, last_accessed)
                    VALUES (?, 0, ?)
                """,
                    (memory_id, datetime.now().isoformat()),
                )

                conn.commit()

                self.logger.info(f"Stored memory: {memory_id}")

                return {
                    "id": memory_id,
                    "content": content,
                    "type": mem_type,
                    "session_id": session_id,
                    "emotion_context": emotion_context,
                    "dharma_tags": dharma_tags,
                    "created_at": datetime.now().isoformat(),
                }

    def recall_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recall memories using full-text search.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of matching memories
        """
        with self.lock:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                search_pattern = f"%{query}%"

                cursor.execute(
                    """
                    SELECT * FROM memories
                    WHERE content LIKE ? OR session_id LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (search_pattern, search_pattern, limit),
                )

                rows = cursor.fetchall()
                results = []

                for row in rows:
                    # Update access stats
                    cursor.execute(
                        """
                        UPDATE access_stats 
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE memory_id = ?
                    """,
                        (datetime.now().isoformat(), row["id"]),
                    )

                    memory = {
                        "id": row["id"],
                        "content": row["content"],
                        "type": row["type"],
                        "session_id": row["session_id"],
                        "emotion_context": json.loads(row["emotion_json"])
                        if row["emotion_json"]
                        else None,
                        "dharma_tags": json.loads(row["tags_json"]) if row["tags_json"] else None,
                        "created_at": row["created_at"],
                    }
                    results.append(memory)

                conn.commit()

                self.logger.info(f"Recalled {len(results)} memories for query: {query}")
                return results

    def search_by_tag(self, tag: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories by tag.

        Args:
            tag: Tag to search for
            limit: Maximum results

        Returns:
            List of memories with the tag
        """
        with self.lock:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT m.* FROM memories m
                    INNER JOIN memory_tags mt ON m.id = mt.memory_id
                    WHERE mt.tag = ?
                    ORDER BY m.created_at DESC
                    LIMIT ?
                """,
                    (tag, limit),
                )

                rows = cursor.fetchall()
                results = []

                for row in rows:
                    memory = {
                        "id": row["id"],
                        "content": row["content"],
                        "type": row["type"],
                        "session_id": row["session_id"],
                        "emotion_context": json.loads(row["emotion_json"])
                        if row["emotion_json"]
                        else None,
                        "dharma_tags": json.loads(row["tags_json"]) if row["tags_json"] else None,
                        "created_at": row["created_at"],
                    }
                    results.append(memory)

                return results

    def get_session_memories(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all memories for a session.

        Args:
            session_id: Session ID

        Returns:
            List of session memories
        """
        with self.lock:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM memories
                    WHERE session_id = ?
                    ORDER BY created_at DESC
                """,
                    (session_id,),
                )

                rows = cursor.fetchall()
                results = []

                for row in rows:
                    memory = {
                        "id": row["id"],
                        "content": row["content"],
                        "type": row["type"],
                        "session_id": row["session_id"],
                        "emotion_context": json.loads(row["emotion_json"])
                        if row["emotion_json"]
                        else None,
                        "dharma_tags": json.loads(row["tags_json"]) if row["tags_json"] else None,
                        "created_at": row["created_at"],
                    }
                    results.append(memory)

                return results

    def cleanup_old_memories(self, days_old: int = 30) -> int:
        """
        Delete memories older than specified days.

        Args:
            days_old: Number of days to keep

        Returns:
            Number of memories deleted
        """
        with self.lock:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()

                cursor.execute(
                    """
                    DELETE FROM memories
                    WHERE created_at < ?
                """,
                    (cutoff_date,),
                )

                deleted_count = cursor.rowcount
                conn.commit()

                self.logger.info(f"Deleted {deleted_count} old memories (>{days_old} days old)")

                return deleted_count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Statistics dictionary
        """
        with self.lock:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) as count FROM memories")
                total_memories = cursor.fetchone()["count"]

                cursor.execute("SELECT COUNT(DISTINCT session_id) as count FROM memories")
                total_sessions = cursor.fetchone()["count"]

                cursor.execute("SELECT COUNT(DISTINCT tag) as count FROM memory_tags")
                total_tags = cursor.fetchone()["count"]

                cursor.execute("SELECT SUM(LENGTH(content)) as size FROM memories")
                size_bytes = cursor.fetchone()["size"] or 0

                cursor.execute("""
                    SELECT COUNT(*) as count, 
                           AVG(access_count) as avg_access
                    FROM access_stats
                """)
                stats_row = cursor.fetchone()

                return {
                    "total_memories": total_memories,
                    "total_sessions": total_sessions,
                    "total_tags": total_tags,
                    "storage_used_bytes": size_bytes,
                    "storage_used_mb": size_bytes / (1024 * 1024),
                    "avg_access_count": stats_row["avg_access"] or 0,
                }

    def get_popular_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most accessed memories.

        Args:
            limit: Number of results

        Returns:
            List of popular memories
        """
        with self.lock:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT m.*, s.access_count
                    FROM memories m
                    INNER JOIN access_stats s ON m.id = s.memory_id
                    ORDER BY s.access_count DESC
                    LIMIT ?
                """,
                    (limit,),
                )

                rows = cursor.fetchall()
                results = []

                for row in rows:
                    memory = {
                        "id": row["id"],
                        "content": row["content"],
                        "type": row["type"],
                        "session_id": row["session_id"],
                        "emotion_context": json.loads(row["emotion_json"])
                        if row["emotion_json"]
                        else None,
                        "dharma_tags": json.loads(row["tags_json"]) if row["tags_json"] else None,
                        "created_at": row["created_at"],
                        "access_count": row["access_count"],
                    }
                    results.append(memory)

                return results
