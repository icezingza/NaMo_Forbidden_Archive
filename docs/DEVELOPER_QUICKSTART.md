# Developer Quickstart

## Setup
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run API
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## Call API
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"text":"สวัสดี","session_id":"demo"}'
```

## API Keys (optional)
ตั้งค่าใน `.env`:
```
NAMO_API_KEYS=key1:public,key2:creator
NAMO_API_DEFAULT_PLAN=public
NAMO_USAGE_LOG_PATH=usage_events.jsonl
```

## Media URLs
- Visual: `/media/visual/{path}`
- Audio: `/media/audio/{path}`
