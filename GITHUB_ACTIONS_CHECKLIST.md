# GitHub Actions Pre-Launch Checklist

## ✅ Before First Push

### Secrets Configuration (Required)
- [ ] Add `DOCKER_HUB_USERNAME` to GitHub repo secrets
- [ ] Add `DOCKER_HUB_TOKEN` to GitHub repo secrets
- [ ] (Optional) Add `CODECOV_TOKEN` for coverage uploads

**How to add:**
1. Go to repo Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Paste each value

### Dockerfile Verification
- [ ] `Dockerfile` has HEALTHCHECK (✓ already added)
- [ ] `Dockerfile.memory` has HEALTHCHECK (✓ updated)
- [ ] Both services expose correct ports (8000, 8081)
- [ ] `/health` endpoint implemented in both services

### Endpoint Implementation
**If not already implemented, add to your FastAPI apps:**

```python
# server.py (for main API)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "namo-api"}

# memory_service.py (for memory service)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "namo-memory"}
```

### Docker Hub Account
- [ ] Account created and accessible
- [ ] Personal Access Token created (Settings > Security > New Access Token)
- [ ] Token scopes: Read, Write, Delete
- [ ] Token does not expire (set to "No expiration" if possible)

### (Optional) Docker Scout
- [ ] Account has signing privileges enabled
- [ ] Can push images with signatures

---

## 🚀 First Run Steps

### 1. Push Changes
```bash
git add .
git commit -m "chore: add enhanced GitHub Actions workflows"
git push origin develop  # Test on develop first
```

### 2. Monitor Workflow
- Go to GitHub repo > Actions tab
- Click "NaMo ACC CI Pipeline"
- Watch for green ✓ checks (should take ~5-10 min)

### 3. Verify Artifacts
- Click completed workflow run
- Go to "Artifacts" section
- Download `sbom-api` and `sbom-memory` files

### 4. Check Security Reports
- If push was to `main`: GitHub repo > Security tab > "Code scanning alerts"
- Should see Docker Scout CVE report

### 5. Verify Docker Hub Push
- Log in to Docker Hub
- Check if images appeared:
  - `username/namo-api:latest`
  - `username/namo-memory:latest`

---

## 🔍 Validation Checklist

| Check | Success Indicator |
|-------|-------------------|
| **Python Lint** | ✓ in Actions (ruff + black passed) |
| **Unit Tests** | ✓ in Actions (pytest passed) |
| **Compose Config** | ✓ in Actions (docker-compose valid) |
| **Docker Build (API)** | ✓ in Actions (image built) |
| **Docker Build (Memory)** | ✓ in Actions (image built) |
| **Health Check (API)** | Container responds to `curl http://localhost:8000/health` |
| **Health Check (Memory)** | Container responds to `curl http://localhost:8081/health` |
| **SBOM Generated** | `.spdx.json` files in Artifacts |
| **Scout Scan** | CVE report shown in annotations |
| **Docker Hub Push** | Images visible in Docker Hub repo (main branch only) |
| **Image Signed** | Cosign signature present (requires main branch) |
| **Security Report** | Scout report in GitHub Security tab (main branch only) |

---

## 🛠️ Troubleshooting

### Workflow Failed: "Health check failed"
**Cause:** `/health` endpoint not implemented or slow to respond
**Fix:** Add endpoints to both services (see "Endpoint Implementation" above)

### Workflow Failed: "Docker Hub authentication failed"
**Cause:** Invalid token or wrong username
**Fix:** 
1. Regenerate token in Docker Hub (Settings > Security)
2. Update GitHub Secrets with new token
3. Verify username spelling

### Workflow Failed: "pytest failed"
**Cause:** Unit tests not passing
**Fix:** Run locally and fix before pushing:
```bash
pip install -r requirements-dev.txt
pytest --tb=short
```

### Health check timeout (20 seconds)
**Cause:** Service takes >5 seconds to start
**Fix:** Increase start period in HEALTHCHECK:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1
```

### SBOM not generated
**Cause:** Docker Scout rate-limit or service unavailable
**Fix:** Retried automatically; not a blocker for deploy

### Scout scan shows many CVEs
**Cause:** Outdated dependencies
**Fix:** Update `requirements.txt` with latest versions
```bash
pip list --outdated
pip install --upgrade <package-name>
```

---

## 📚 Useful Commands

### Test locally before pushing
```bash
# Lint
ruff check .
black --check .

# Tests
pytest --tb=short

# Docker build
docker build -f Dockerfile -t namo-api:test .
docker run -d -p 8000:8000 namo-api:test
curl http://localhost:8000/health
docker stop <container-id>
```

### Check workflow syntax (if GitHub CLI installed)
```bash
gh workflow list
gh workflow view ci.yml
```

### Manual workflow trigger (GitHub CLI)
```bash
gh workflow run build-cloud.yml
gh workflow view ci.yml --log
```

---

## 🎯 After First Successful Run

- [ ] Celebrate! 🎉
- [ ] Push to `main` branch
- [ ] Verify images in Docker Hub
- [ ] Check security report in GitHub Security tab
- [ ] Share workflow status badge in README (optional)

```markdown
## CI/CD Status
![CI Pipeline](https://github.com/YOUR_ORG/NaMo_Forbidden_Archive/actions/workflows/ci.yml/badge.svg)
```

---

## 📞 Support

- **GitHub Actions Docs:** https://docs.github.com/actions
- **Docker Scout:** https://docs.docker.com/scout/
- **Cosign:** https://docs.sigstore.dev/cosign/
