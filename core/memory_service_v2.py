"""
Memory Service V2 (Neo4j AuraDB Cloud Graph & Memory Consolidation)
NRE v6.0.0 Sovereign Brain Architecture
"""

from __future__ import annotations

import logging
import os
from typing import Any

try:
    from neo4j import GraphDatabase, Driver
except ImportError:
    GraphDatabase = None
    Driver = None

logger = logging.getLogger("MemoryServiceV2")


class Neo4jMemoryService:
    """Sovereign Graph Memory Service using Neo4j AuraDB (Free Tier Compatible)."""

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver: Driver | None = None

        if GraphDatabase and self.uri and self.password:
            try:
                self.driver = GraphDatabase.driver(
                    self.uri, auth=(self.username, self.password)
                )
                logger.info("[Neo4jMemoryService] Connected to Neo4j AuraDB at %s", self.uri)
            except Exception as exc:
                logger.warning("[Neo4jMemoryService] Connection failed (%s), running in offline mode.", exc)
        else:
            logger.info("[Neo4jMemoryService] Neo4j credentials missing or driver not installed. Offline mode.")

    def close(self):
        if self.driver:
            self.driver.close()

    def record_turn(
        self,
        session_id: str,
        user_input: str,
        response_text: str,
        emotion_state: dict[str, float] | None = None,
        beat: str = "tease",
        tension: float = 0.0,
    ) -> bool:
        """Stores a conversation turn and 5D emotion state as connected graph nodes."""
        if not self.driver:
            return False

        query = """
        MERGE (s:Session {id: $session_id})
        CREATE (t:Turn {
            timestamp: datetime(),
            user_input: $user_input,
            response: $response_text,
            beat: $beat,
            tension: $tension
        })
        MERGE (s)-[:HAS_TURN]->(t)
        WITH t
        CREATE (e:EmotionState {
            arousal: $arousal,
            trust: $trust,
            passion: $passion,
            temperament: $temperament,
            resonance: $resonance
        })
        CREATE (t)-[:EXPRESSED]->(e)
        """
        emo = emotion_state or {}
        params = {
            "session_id": session_id,
            "user_input": user_input,
            "response_text": response_text,
            "beat": beat,
            "tension": float(tension),
            "arousal": float(emo.get("arousal", 0.0)),
            "trust": float(emo.get("trust", 0.5)),
            "passion": float(emo.get("passion", 0.5)),
            "temperament": float(emo.get("temperament", 0.5)),
            "resonance": float(emo.get("resonance", 0.5)),
        }

        try:
            with self.driver.session() as session:
                session.run(query, params)
            return True
        except Exception as exc:
            logger.error("[Neo4jMemoryService] Error recording turn: %s", exc)
            return False

    def consolidate_memories(self, session_id: str = "default") -> dict[str, Any]:
        """Consolidates recent turn nodes into a summarized LongTermMemory node (Dream Loop)."""
        if not self.driver:
            return {"status": "skipped", "reason": "no_neo4j_driver"}

        query = """
        MATCH (s:Session {id: $session_id})-[:HAS_TURN]->(t:Turn)
        WHERE NOT (t)-[:CONSOLIDATED]->()
        RETURN t.user_input AS input, t.response AS resp, t.beat AS beat, t.tension AS tension
        ORDER BY t.timestamp ASC
        LIMIT 20
        """
        try:
            with self.driver.session() as session:
                results = session.run(query, {"session_id": session_id})
                records = [record.data() for record in results]

            if not records:
                return {"status": "completed", "consolidated_turns": 0}

            # Create summary milestone node
            create_summary_query = """
            MATCH (s:Session {id: $session_id})
            CREATE (m:LongTermMemory {
                consolidated_at: datetime(),
                turn_count: $turn_count,
                summary: $summary
            })
            MERGE (s)-[:HAS_MEMORY]->(m)
            WITH m
            MATCH (s:Session {id: $session_id})-[:HAS_TURN]->(t:Turn)
            WHERE NOT (t)-[:CONSOLIDATED]->()
            LIMIT $turn_count
            CREATE (t)-[:CONSOLIDATED]->(m)
            """
            summary_text = f"Consolidated {len(records)} turns. Peak tension: {max((r['tension'] for r in records), default=0.0)}"
            with self.driver.session() as session:
                session.run(create_summary_query, {
                    "session_id": session_id,
                    "turn_count": len(records),
                    "summary": summary_text
                })

            return {"status": "success", "consolidated_turns": len(records), "summary": summary_text}

        except Exception as exc:
            logger.error("[Neo4jMemoryService] Memory consolidation error: %s", exc)
            return {"status": "error", "message": str(exc)}
