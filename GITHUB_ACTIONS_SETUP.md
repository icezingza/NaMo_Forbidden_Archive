# GitHub Actions Setup Guide for NaMo Forbidden Archive

## Overview

Your project now has enhanced GitHub Actions workflows for comprehensive CI/CD with Docker supply chain security.

## Workflows Installed

### 1. **ci.yml** (NaMo ACC CI Pipeline)
Main CI pipeline triggered on push/PR to `main` and `develop` branches.

**Jobs:**
- `test` — Python linting (ruff, black), unit tests with coverage, Codecov upload
- `validate-compose` — Docker Compose configuration validation
- `docker-build-test` — Multi-service Docker builds (API + Memory) with:
  - Container health endpoint checks
  - SBOM (Software Bill of Materials) generation
  - CVE vulnerability scanning via Docker Scout
  - PR comparison reports
- `docker-push` — Push to Docker Hub on `main` branch with post-push security scanning

**Key Features:**
✅ Health check validation (waits for `/health` endpoint on ports 8000 & 8081)
✅ SBOM artifacts uploaded for each build
✅ Docker Scout CVE scanning (critical/high severity)
✅ GitHub Actions cache for layer caching
✅ Conditional deployment (only on `main` branch)

**Environment Variables Required:**
- `DOCKER_HUB_USERNAME` (secret)
- `DOCKER_HUB_TOKEN` (secret)
- `CODECOV_TOKEN` (secret, optional)

---

### 2. **security-scanning.yml** (Docker Image Security & Signing)
Runs after main CI pipeline completes on `main` branch.

**Jobs:**
- `sign-and-attest` — Keyless Cosign image signing using OIDC
- `deploy-security-report` — Generates SARIF report and uploads to GitHub Security tab

**Key Features:**
✅ Keyless signing (no key management needed)
✅ OIDC trust model (GitHub-to-Sigstore-to-Docker Hub)
✅ Attestations with build metadata
✅ Automatic GitHub Security tab integration
✅ Verifiable supply chain (cosign verify)

**Setup Required:**
1. Ensure Docker Hub account has signing enabled
2. No additional secrets needed (uses GitHub OIDC token)

---

### 3. **build-cloud.yml** (Multi-Platform Builds)
Builds for multiple architectures (AMD64 + ARM64) with optional manual trigger.

**Jobs:**
- `multi-platform-build` — Builds API & Memory images for `linux/amd64,linux/arm64`
- `sbom-generation` — Generates SBOMs for each platform

**Key Features:**
✅ Multi-platform support (intel/arm easily extended)
✅ Manual trigger via GitHub UI with custom platform selection
✅ Automatic trigger on Dockerfile changes
✅ GHA cache reuse across platforms

**Trigger Methods:**
- Manual: Go to Actions > Docker Build Cloud Setup > Run workflow
- Automatic: Push changes to `Dockerfile` or `requirements*.txt`

---

## Required GitHub Secrets

Add these in your GitHub repo settings (Settings > Secrets and variables > Actions):

```
DOCKER_HUB_USERNAME = your_dockerhub_username
DOCKER_HUB_TOKEN    = your_dockerhub_personal_access_token
CODECOV_TOKEN       = (optional) your_codecov_token
```

### Generate Docker Hub Personal Access Token:
1. Docker Hub > Account Settings > Security > New Access Token
2. Scopes: Read, Write, Delete
3. Copy and paste into GitHub Secrets

---

## Workflow Execution Timeline

### On PR to develop/main:
```
test (lint, pytest) ─┐
                    ├─→ docker-push (conditional: main only)
validate-compose ───┤
                    └─→ security-scanning (sign & attest)
docker-build-test ──┘
```

### On push to main:
All jobs above run + SBOM artifacts uploaded + Scout report to Security tab

---

## Health Check Configuration

Both Dockerfiles now include:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1
```

The workflow waits up to 20 seconds for containers to become healthy before proceeding.

---

## Scout/SBOM Artifacts

After each build, SBOM files are generated and uploaded to Actions Artifacts:
- `sbom-api.spdx.json` — API service dependencies in SPDX format
- `sbom-memory.spdx.json` — Memory service dependencies

Download from Actions > [workflow run] > Artifacts to audit supply chain.

---

## Image Verification (Post-Deployment)

After images are pushed, verify signatures:

```bash
# Install cosign (if not already installed)
curl -sSL https://github.com/sigstore/cosign/releases/download/v2.2.0/cosign-linux-amd64 -o cosign
chmod +x cosign

# Verify image signature
./cosign verify --certificate-identity-regexp="https://github.com/YOUR_ORG/NaMo_Forbidden_Archive" \
  docker_hub_username/namo-api:latest

# Verify attestation
./cosign verify-attestation --certificate-identity-regexp="https://github.com/YOUR_ORG/NaMo_Forbidden_Archive" \
  docker_hub_username/namo-api:latest
```

---

## Monitoring & Debugging

### View workflow runs:
- GitHub repo > Actions tab
- Click workflow name > Click run

### Common issues:
- **Health check timeout**: Ensure `/health` endpoint exists and responds in <10s
- **Docker Hub auth failed**: Verify token is not expired (rotate if >1 year old)
- **Cosign signature failed**: Ensure Docker Hub account has signing enabled
- **SBOM generation skipped**: Docker Scout may have rate-limited; retried automatically

### Logs:
All jobs output to GitHub Actions logs (green ✓ = passed, red ✗ = failed)

---

## Next Steps

1. **Push a test commit** to see workflows in action:
   ```bash
   git add .github/workflows/*.yml
   git commit -m "chore: enhance CI/CD with Docker security"
   git push origin main
   ```

2. **Monitor first run** in GitHub Actions tab

3. **Configure Docker Hub** for image signing (if not auto-enabled)

4. **Set up Build Cloud** (optional):
   - Visit https://app.docker.com/settings/build-cloud
   - Create builder and note builder ID
   - Add to GitHub Actions if deploying multi-platform

5. **Review security reports** in GitHub Security tab after first push to main

---

## Quick Reference: Manual Workflow Triggers

```bash
# Trigger multi-platform build via GitHub CLI (if installed)
gh workflow run build-cloud.yml -f platforms="linux/amd64,linux/arm64,linux/arm/v7"

# Or use GitHub UI:
# Actions > Docker Build Cloud Setup & Multi-Platform Build > Run workflow
```

---

## Files Modified

- `.github/workflows/ci.yml` — Enhanced with health checks, SBOM, Scout reports
- `.github/workflows/security-scanning.yml` — NEW: Cosign signing + SARIF reports
- `.github/workflows/build-cloud.yml` — NEW: Multi-platform builds + SBOM
- `Dockerfile.memory` — Added HEALTHCHECK + env vars

---

## Support

For issues:
- Docker Scout docs: https://docs.docker.com/scout/
- Cosign docs: https://docs.sigstore.dev/cosign/overview/
- GitHub Actions docs: https://docs.github.com/actions
