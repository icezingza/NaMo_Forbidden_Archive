# NaMo Forbidden Archive (ACC) - Telegram Bot Setup Guide

## Full System Telegram Integration

### Prerequisites
- Docker running with the ACC container (`namo-acc:8080`)
- Telegram bot created via @BotFather (`t.me/Vipha_ACC_bot`)
- TELEGRAM_BOT_TOKEN set in `.env`
- Public URL/Domain (HTTPS required by Telegram)

---

## Step 1: Get Public HTTPS URL

### Option A: ngrok (Local Development)
```bash
# Download from https://ngrok.com/download
# Then run:
ngrok http 8080
# You'll get: https://xxx-xxx-xxx.ngrok.io
```

### Option B: Custom Domain (Production)
- Point your domain's DNS to your server
- Get SSL certificate (Let's Encrypt via Certbot)
- Setup reverse proxy (nginx/caddy)

### Option C: Cloud Deployment
- AWS Lambda + API Gateway
- Google Cloud Run
- Azure Functions
- Railway, Render, Fly.io

---

## Step 2: Setup Environment

**Update `.env`:**
```env
TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
BACKEND_URL=https://your-webhook-url.com
```

**Update `docker-compose.yml` (if using):**
```yaml
telegram-bot:
  environment:
    - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    - BACKEND_URL=${BACKEND_URL}
```

---

## Step 3: Register Webhook

### Using Python Script (Recommended)
```bash
cd projects-NaMo-Forbidden-Archive

# Set bot token
export TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"

# Register webhook
python setup_telegram.py --webhook-url https://your-domain.com/webhook/telegram

# Check webhook info
python setup_telegram.py --info

# Delete webhook (if needed)
python setup_telegram.py --delete
```

### Using cURL
```bash
curl -X POST \
  https://api.telegram.org/botYOUR_TOKEN/setWebhook \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://your-domain.com/webhook/telegram"}'
```

### Using REST API Endpoint
```bash
curl -X POST http://localhost:8081/telegram/register-webhook \
  -H 'Content-Type: application/json' \
  -d '{"webhook_url":"https://your-domain.com/webhook/telegram"}'
```

---

## Step 4: Test Telegram Bot

1. Open Telegram
2. Search for `@Vipha_ACC_bot`
3. Send `/start`
4. Expected: Welcome message with system intro
5. Send any message to chat with Vipha
6. Send `/reset` to reset session

---

## API Endpoints

### REST Endpoints (for programmatic use)
- `GET /` - Health check
- `POST /session/chat` - Chat with ACC
- `GET /session/{session_id}` - Get session state
- `POST /session/reset` - Reset session

### Telegram Endpoints
- `POST /webhook/telegram` - Telegram webhook receiver
- `POST /telegram/register-webhook` - Register webhook
- `GET /telegram/webhook-info` - Get webhook status

---

## Telegram Commands

| Command | Action |
|---------|--------|
| `/start` | Initialize conversation |
| `/reset` | Reset relationship to Stage 1 |
| Regular text | Chat with Vipha |

---

## Response Format

Each message from Vipha includes:
- **Narrative**: Her roleplay response
- **Emotional State**: 5D emotion metrics (Arousal, Trust, Passion, Temperament, Resonance)
- **Hook**: Question/statement to prompt next turn

Example:
```
*Her narrative here...*

💌 *Emotional State:*
  • Arousal: 45.0%
  • Trust: 60.0%
  • Passion: 35.0%

_Her hook question here..._
```

---

## Architecture

```
┌─────────────────┐
│  Telegram User  │
└────────┬────────┘
         │ Message
         │
┌────────▼─────────────────────┐
│  Telegram Bot API             │
│  (t.me/Vipha_ACC_bot)         │
└────────┬─────────────────────┘
         │ Webhook POST
         │ https://your-domain.com/webhook/telegram
         │
┌────────▼──────────────────────────┐
│  ACC Server (Docker:8080)         │
│  • FastAPI + Uvicorn              │
│  • server.py (webhook handler)    │
│  • LLMProvider (Gemini 1.5 Flash) │
│  • MemoryService (Session state)  │
└────────┬──────────────────────────┘
         │
┌────────▼──────────────────────────┐
│  External Services                │
│  • Google Gemini AI               │
│  • Elevenlabs (Voice synthesis)   │
│  • Local Storage (Session memory) │
└───────────────────────────────────┘
```

---

## Session Management

Each Telegram user (`user_id`) gets a persistent session:
- **Session ID**: Telegram `user_id`
- **State Storage**: Local JSON files (`/tmp/sessions/`) or GCS
- **Persistence**: Relationships and emotions persist across sessions
- **Reset**: `/reset` command resets to Stage 1

Example session file: `/tmp/sessions/{user_id}.json`
```json
{
  "session_id": "123456789",
  "relationship_stage": 2,
  "emotion_state": {
    "arousal": 0.45,
    "trust": 0.60,
    "passion": 0.35,
    "temperament": 0.80,
    "resonance": 0.50
  },
  "history": [...]
}
```

---

## Troubleshooting

### Webhook not receiving messages
- Check webhook URL is HTTPS (required by Telegram)
- Verify firewall/port forwarding
- Test: `python setup_telegram.py --info`

### Bot not responding
- Check container logs: `docker logs namo-acc`
- Verify TELEGRAM_BOT_TOKEN in `.env`
- Confirm Gemini API key is valid

### Session not persisting
- Check LOCAL_STORAGE_DIR exists
- Verify file permissions: `ls -la /tmp/sessions/`
- Try GCS: set `USE_GCS=true` + `GCS_BUCKET_NAME`

### Rate limiting
- Telegram: ~30 msgs/sec max
- Gemini: Check quota in Google Cloud Console
- Redis queue (optional) for scaling

---

## Production Deployment

### Docker Compose
```bash
cd C:\Users\icezi\Downloads\Github\ repo\NaMo_Forbidden_Archive
docker compose up -d --build
```

### Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
    }
}
```

### Environment Variables
```bash
TELEGRAM_BOT_TOKEN=YOUR_TOKEN
GEMINI_API_KEY=YOUR_KEY
USE_GCS=true
GCS_BUCKET_NAME=namo-sessions
LOCAL_STORAGE_DIR=/data/sessions
```

---

## Security Notes

⚠️ **Important:**
- Never commit `.env` with real tokens to Git
- Use secrets manager for production (AWS Secrets, Vault, etc.)
- Validate all Telegram updates (verify bot token signature)
- Rate limit per user to prevent abuse
- Sanitize user input before passing to Gemini

---

## Support & Debugging

Enable debug logging:
```python
# In server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

View logs:
```bash
docker logs -f namo-acc
```

---

**Ready to chat? Open Telegram and find `@Vipha_ACC_bot`! 🌹**
