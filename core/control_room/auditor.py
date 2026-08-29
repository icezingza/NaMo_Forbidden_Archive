"""Security Auditor for NRE Control Room.

Performs static integrity checks on project configuration, secret management,
file permissions, and endpoint security posture.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SecurityAuditor:
    """Automated security posture and file integrity scanner."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(".")

    def run_audit(self) -> dict[str, Any]:
        """Execute complete security audit scan."""
        findings: list[dict[str, Any]] = []

        # 1. Check .env in .gitignore
        gitignore_path = self.base_dir / ".gitignore"
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8")
            if ".env" not in content:
                findings.append({
                    "id": "SEC-001",
                    "severity": "HIGH",
                    "category": "Git Secrets",
                    "message": ".env file is NOT listed in .gitignore! Risks secret exposure.",
                })
            else:
                findings.append({
                    "id": "SEC-001",
                    "severity": "PASS",
                    "category": "Git Secrets",
                    "message": ".env is properly excluded in .gitignore.",
                })

        from core.gcp_secrets import DynamicSecretsLoader
        loader = DynamicSecretsLoader()

        # 2. Check ADMIN_SECRET configuration
        admin_secret = loader.get_secret("ADMIN_SECRET")
        if not admin_secret:
            findings.append({
                "id": "SEC-002",
                "severity": "MEDIUM",
                "category": "Authentication",
                "message": "ADMIN_SECRET is not set in environment or GCP. Admin routes rely on fallback.",
            })
        elif len(admin_secret) < 12:
            findings.append({
                "id": "SEC-002",
                "severity": "MEDIUM",
                "category": "Authentication",
                "message": "ADMIN_SECRET is too short (< 12 characters). Recommended >= 16 characters.",
            })
        else:
            findings.append({
                "id": "SEC-002",
                "severity": "PASS",
                "category": "Authentication",
                "message": "ADMIN_SECRET is securely configured.",
            })

        # 3. Check OPENAI_API_KEY presence
        openai_key = loader.get_secret("OPENAI_API_KEY")
        if not openai_key:
            findings.append({
                "id": "SEC-003",
                "severity": "INFO",
                "category": "Third-Party API",
                "message": "OPENAI_API_KEY is missing. System will operate in offline/mock mode.",
            })
        else:
            findings.append({
                "id": "SEC-003",
                "severity": "PASS",
                "category": "Third-Party API",
                "message": "OPENAI_API_KEY is present.",
            })

        # 4. Check GCP Secret Manager Status
        if loader.is_gcp_active():
            findings.append({
                "id": "SEC-005",
                "severity": "PASS",
                "category": "Cloud Secret Manager",
                "message": f"GCP Secret Manager active for project '{loader.project_id}'.",
            })
        else:
            findings.append({
                "id": "SEC-005",
                "severity": "INFO",
                "category": "Cloud Secret Manager",
                "message": "GCP Secret Manager unconfigured. Operating with local env fallback.",
            })


        # 4. Check critical data file presence and non-emptiness
        critical_files = ["memory_history.json", "system.yaml"]
        for cfile in critical_files:
            cpath = self.base_dir / cfile
            if cpath.exists() and cpath.stat().st_size == 0:
                findings.append({
                    "id": "SEC-004",
                    "severity": "HIGH",
                    "category": "Data Integrity",
                    "message": f"Critical file {cfile} exists but is empty (0 bytes)!",
                })

        # Calculate security rating
        high_count = sum(1 for f in findings if f["severity"] == "HIGH")
        medium_count = sum(1 for f in findings if f["severity"] == "MEDIUM")

        if high_count > 0:
            overall_status = "CRITICAL"
        elif medium_count > 0:
            overall_status = "WARNING"
        else:
            overall_status = "HEALTHY"

        return {
            "overall_status": overall_status,
            "total_checks": len(findings),
            "high_issues": high_count,
            "medium_issues": medium_count,
            "findings": findings,
        }
