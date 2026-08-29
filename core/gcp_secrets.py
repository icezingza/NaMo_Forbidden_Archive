"""Dynamic Secret Manager Connector for NRE Sovereign Edition.

Supports fetching secrets dynamically from GCP Secret Manager when available,
with graceful fallback to environment variables and .env settings.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class DynamicSecretsLoader:
    """Dynamic secret resolver with GCP Secret Manager support & local fallback."""

    def __init__(self, project_id: str | None = None) -> None:
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self._gcp_client: Any | None = None
        self._init_client()

    def _init_client(self) -> None:
        """Attempt to initialize GCP Secret Manager client if dependencies exist."""
        if not self.project_id:
            return

        try:
            from google.cloud import secretmanager

            self._gcp_client = secretmanager.SecretManagerServiceClient()
            logger.info(
                "GCP SecretManagerServiceClient initialized for project: %s", self.project_id
            )
        except Exception as err:
            logger.debug(
                "GCP SecretManager client unavailable (%s). Falling back to env vars.", err
            )
            self._gcp_client = None

    def get_secret(self, secret_id: str, default: str | None = None) -> str | None:
        """Fetch secret value from GCP Secret Manager or fallback to os.getenv.

        Args:
            secret_id: Name of secret (e.g. ADMIN_SECRET, OPENAI_API_KEY).
            default: Optional fallback default value.

        Returns:
            Resolved secret string or default.
        """
        # 1. Try GCP Secret Manager if client is available
        if self._gcp_client and self.project_id:
            try:
                name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
                response = self._gcp_client.access_secret_version(request={"name": name})
                secret_val = response.payload.data.decode("UTF-8").strip()
                if secret_val:
                    return secret_val
            except Exception as err:
                logger.warning(
                    "Failed to access GCP secret '%s': %s. Using env fallback.", secret_id, err
                )

        # 2. Fallback to local environment variable / .env
        env_val = os.getenv(secret_id)
        if env_val is not None:
            return env_val

        return default

    def is_gcp_active(self) -> bool:
        """Check if GCP Secret Manager client is initialized and active."""
        return self._gcp_client is not None
