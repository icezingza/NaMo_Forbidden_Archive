"""BehavioralAnalyticsService — periodic Neo4j-based user-behavior analysis.

Runs as a standalone process.  Reads Neo4j connection settings from environment
variables (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD) so that no secrets are
hard-coded in source.  Results are printed to stdout; in a production setup
they would be published to a message queue (e.g. Redis Streams) for the
Cognitive Core to consume.
"""

import os
import time

import pandas as pd
from neo4j import GraphDatabase


class BehavioralAnalyticsService:
    """Analyses user behaviour from the Neo4j graph, generates features,
    and predicts the user's next anticipated intent.

    Runs periodically via the ``run_loop()`` method.
    """

    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str) -> None:
        self._driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        print("[BehavioralAnalyticsService] Initialized.")

    def close(self) -> None:
        self._driver.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_features(self, tx, user_id: str) -> pd.DataFrame:
        """Cypher query: pull the 100 most recent interactions for a user.

        In production the query will be more complex, computing centrality
        scores, temporal features, and sentiment trajectories directly in Cypher.
        """
        query = (
            "MATCH (u:User {id: $user_id})-[r:INTERACTED_WITH]->(c:Character) "
            "RETURN type(r) AS interaction_type, r.timestamp AS timestamp, "
            "c.name AS character_name "
            "ORDER BY r.timestamp DESC LIMIT 100"
        )
        results = tx.run(query, user_id=user_id)
        df = pd.DataFrame([record.data() for record in results])
        # --- Feature Engineering ---
        # (e.g. compute frequency, recency, interaction-sequence ordering)
        print(
            f"[BehavioralAnalyticsService] Extracted {len(df)} interaction records "
            f"for user {user_id}."
        )
        return df

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict_intent(self, user_id: str = "ไอซ์") -> str | None:
        """Return the predicted next intent for *user_id*, or None if no data."""
        with self._driver.session() as session:
            feature_df = session.read_transaction(self._extract_features, user_id)

        if feature_df.empty:
            print(f"[BehavioralAnalyticsService] No data for user {user_id}.")
            return None

        # Placeholder: swap for a real joblib / ONNX model prediction call.
        # predicted_intent = self.prediction_model.predict(feature_df)
        predicted_intent = "Anticipated_Intent: Cuckolding"
        print(
            f"[BehavioralAnalyticsService] Predicted next intent for user {user_id}: "
            f"{predicted_intent}"
        )
        return predicted_intent

    def run_loop(self, user_id: str = "ไอซ์", interval_seconds: int = 60) -> None:
        """Block and run analysis every *interval_seconds* seconds.

        In production, publish ``predict_intent()`` results to a message queue
        (e.g. Redis Streams / RabbitMQ) so the Cognitive Core can consume them
        as Anticipatory Impulses without tight coupling.
        """
        try:
            while True:
                print("\n--- Running Periodic Behavioral Analysis ---")
                self.predict_intent(user_id=user_id)
                time.sleep(interval_seconds)
        finally:
            self.close()


if __name__ == "__main__":
    # Connection settings must come from environment variables — never hardcode.
    _uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    _user = os.environ.get("NEO4J_USER", "neo4j")
    _password = os.environ.get("NEO4J_PASSWORD", "")

    if not _password:
        raise RuntimeError(
            "NEO4J_PASSWORD environment variable is not set. "
            "Set it before starting BehavioralAnalyticsService."
        )

    analyzer = BehavioralAnalyticsService(_uri, _user, _password)
    analyzer.run_loop()
