"""Unit tests for DynamicSecretsLoader."""

from __future__ import annotations

import os

from core.gcp_secrets import DynamicSecretsLoader


def test_dynamic_secrets_loader_fallback():
    os.environ["TEST_SECRET_KEY"] = "super_secret_value_123"
    loader = DynamicSecretsLoader()

    val = loader.get_secret("TEST_SECRET_KEY")
    assert val == "super_secret_value_123"

    fallback_val = loader.get_secret("NON_EXISTENT_KEY", default="default_val")
    assert fallback_val == "default_val"


def test_gcp_active_status():
    loader = DynamicSecretsLoader()
    # GCP Secret Manager won't be active without real GCP creds/project
    assert isinstance(loader.is_gcp_active(), bool)
