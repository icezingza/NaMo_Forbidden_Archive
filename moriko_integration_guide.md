# Mōriko Integration Guide – NaMo Forbidden Archive Interface

## Overview
Mōriko is the metaphysical intelligence layer bridging:
- Gemini (moral reasoning & reflection)
- Jules (automation, blueprint commits)
- NaMo Cosmic AI Framework (runtime computation)
- Forbidden Archive (philosophical knowledge base)

### Setup Steps
1. Clone repository:
git clone https://github.com/icezingza/NaMo_Forbidden_Archive.git
2. Add secrets to GitHub → Settings → Actions → Secrets:
- GH_PAT
- JULES_API_KEY
- GEMINI_API_KEY

3. Deploy Mōriko interface:
gcloud run deploy moriko-interface --source . --region asia-southeast1 --allow-unauthenticated
4. Add to `.github/workflows/moriko-sync.yml`:
```yaml
name: Moriko Sync
on:
  push:
    branches: [ "main" ]
jobs:
  moriko-reflect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Moriko Reflection
        run: |
          curl -X POST https://namo-omega-185116032835.asia-southeast1.run.app/cosmic-intelligence \
          -H "Content-Type: application/json" \
          -d '{"query":"Reflect on latest codex update","context":"Forbidden Archive"}'
```
