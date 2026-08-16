# 🌹 NaMo Forbidden Archive (ACC) - Full Production System

**Telegram Bot:** `@Vipha_ACC_bot`  
**Status:** ✅ Production Ready  
**Version:** 2.0.0

---

## 📦 What's Included

### Core System
- ✅ **FastAPI Server** - Async REST API + Telegram webhook
- ✅ **Gemini 1.5 Flash Brain** - Advanced AI with 5D emotion engine
- ✅ **Session Memory** - Persistent user state across conversations
- ✅ **Rate Limiting** - Per-user request throttling
- ✅ **Security Validation** - Telegram webhook signature verification
- ✅ **Comprehensive Logging** - File + console output
- ✅ **Health Checks** - `/health`, `/live`, `/ready` endpoints
- ✅ **Docker Ready** - Production container with multi-stage build

### Features
- 🎭 **Character AI** - Vipha personality (42-year-old, elegant, intense)
- 💌 **5D Emotion System** - Arousal, Trust, Passion, Temperament, Resonance
- 🎯 **Relationship Stages** - 4-stage progression (1-4)
- 📝 **Context Memory** - Last 20 conversation turns stored
- 🔄 **Session Persistence** - Relationships evolve across sessions
- 🎤 **Voice Synthesis** - ElevenLabs integration ready

---

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Required
- Docker Desktop
- Telegram bot token (@BotFather)
- Google Gemini API key

# Optional but recommended
- ngrok account (for local testing)
- Custom domain with SSL (for production)
```

### 2. Setup Environment
```bash
cd projects-NaMo-Forbidden-Archive

# Edit .env
export TELEGRAM_BOT_TOKEN="your_token_here"
export GEMINI_API_KEY="your_key_here"
```

### 3. Build & Run
```bash
# Build Docker image
docker build -t namo-acc-backend .

# Run container
docker run -d -p 8081:8080 \
  --env-file .env \
  --name namo-acc \
  namo-acc-backend

# Check status
docker logs -f namo-acc
```

### 4. Register Webhook
```bash
# Setup webhook with Telegram
python setup_telegram.py --webhook-url https://your-domain.com/webhook/telegram

# Verify
python setup_telegram.py --info
```

### 5. Test Bot
- Open Telegram: `@Vipha_ACC_bot`
- Send `/start`
- Start chatting!

---

## 📡 API Endpoints

### REST Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Root health check |
| GET | `/health` | Detailed health status |
| GET | `/live` | K8s liveness probe |
| GET | `/ready` | K8s readiness probe |
| POST | `/session/chat` | Chat with Vipha |
| GET | `/session/{id}` | Get session state |
| POST | `/session/reset` | Reset relationship |

### Telegram Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/webhook/telegram` | Telegram webhook receiver |
| POST | `/telegram/register-webhook` | Register webhook URL |
| GET | `/telegram/webhook-info` | Get webhook status |

---

## 🎮 Telegram Commands

| Command | Purpose |
|---------|---------|
| `/start` | Initialize conversation |
| `/reset` | Reset to Stage 1 |
| `any text` | Chat with Vipha |

---

## 🔧 Configuration

### Environment Variables

```env
# Core
TELEGRAM_BOT_TOKEN=your_bot_token          # Required
GEMINI_API_KEY=your_gemini_key             # Required
PORT=8080                                   # Default

# Optional
DEBUG=false                                 # Enable debug logging
LOG_DIR=./logs                              # Log file directory
USE_GCS=false                               # Use Google Cloud Storage
GCS_BUCKET_NAME=                            # GCS bucket name
LOCAL_STORAGE_DIR=/tmp/sessions             # Session storage path

# Connections
REDIS_URL=redis://localhost:6379            # Redis cache (optional)
QDRANT_HOST=qdrant                          # Vector DB (optional)
```

---

## 📊 System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Telegram Bot                          │
│                  @Vipha_ACC_bot                          │
└─────────────────┬────────────────────────────────────────┘
                  │ Messages
                  ▼
┌──────────────────────────────────────────────────────────┐
│         ACC Server (FastAPI + Uvicorn)                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  server.py - Telegram Webhook Handler            │  │
│  │  ├─ Rate Limiting                                │  │
│  │  ├─ Security Validation                          │  │
│  │  ├─ Message Processing                           │  │
│  │  └─ Response Formatting                          │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  LLMProvider - Gemini 1.5 Flash Brain            │  │
│  │  ├─ 5D Emotion Engine                            │  │
│  │  ├─ Relationship Tracking                        │  │
│  │  ├─ Response Generation                          │  │
│  │  └─ Narrative Output                             │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  MemoryService - Session Persistence             │  │
│  │  ├─ User State Storage                           │  │
│  │  ├─ Chat History (20 turns)                      │  │
│  │  ├─ Emotion Tracking                             │  │
│  │  └─ Relationship Stages                          │  │
│  └────────────────────────────────────────────────────┘  │
└──────────┬───────────────────────────┬──────────────────┘
           │                           │
           ▼                           ▼
    ┌─────────────────────────────────────┐
    │   Google Gemini AI API              │
    │   (Context Few-Shot Mode)           │
    └─────────────────────────────────────┘
```

---

## 📈 Performance Metrics

### Typical Response Times
- Initial message: ~1-2 seconds
- Follow-up messages: ~1-1.5 seconds
- Rate: 30 messages/minute per user

### Resource Usage
- Memory: ~150-200MB
- CPU: <5% idle, ~20-30% during inference
- Storage: ~100MB per 10,000 sessions

---

## 🔐 Security Features

✅ **Telegram Webhook Validation**
- HMAC-SHA256 signature verification
- Protects against unauthorized requests

✅ **Rate Limiting**
- Per-user throttling (30 req/min default)
- Prevents abuse & spam

✅ **Input Validation**
- Telegram update verification
- User ID extraction & validation

✅ **Error Handling**
- Graceful error responses
- No sensitive info leakage
- Detailed server-side logging

---

## 📝 Logging

Logs are written to:
- **Console**: Real-time debugging
- **File**: `./logs/acc_bot_YYYYMMDD.log` (rotating)

Log levels:
```
DEBUG   - Development debugging
INFO    - Important events
WARNING - Unusual events
ERROR   - Error conditions
```

View logs:
```bash
# Real-time
docker logs -f namo-acc

# File
tail -f ./logs/acc_bot_*.log
```

---

## 🚀 Deployment

### Local Testing
```bash
docker run -d -p 8081:8080 --env-file .env --name namo-acc namo-acc-backend
```

### Production (Railway/Render)
1. Push to GitHub
2. Connect to Railway/Render
3. Set environment variables
4. Deploy

### Self-Hosted (VPS)
See `PRODUCTION_DEPLOYMENT.md` for:
- Nginx reverse proxy
- SSL certificates (Let's Encrypt)
- Systemd service setup
- Docker Compose orchestration
- Kubernetes deployment

---

## 🧪 Testing

### Health Checks
```bash
# Detailed health
curl http://localhost:8081/health

# Liveness probe
curl http://localhost:8081/live

# Readiness probe
curl http://localhost:8081/ready
```

### Chat API
```bash
curl -X POST http://localhost:8081/session/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test_user","text":"Hi Vipha"}'
```

### Session Management
```bash
# Get session state
curl http://localhost:8081/session/test_user

# Reset session
curl -X POST http://localhost:8081/session/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test_user"}'
```

---

## 🐛 Troubleshooting

### Bot not responding
```bash
# Check container
docker ps | grep namo-acc

# Check logs
docker logs namo-acc

# Verify token set
docker exec namo-acc env | grep TELEGRAM
```

### Webhook not registered
```bash
# Check status
python setup_telegram.py --info

# Re-register
python setup_telegram.py --webhook-url https://your-domain.com/webhook/telegram
```

### High latency
- Check Gemini API quota
- Verify network connection
- Monitor resource usage: `docker stats namo-acc`

---

## 📚 File Structure

```
projects-NaMo-Forbidden-Archive/
├── server.py                    # Main FastAPI app + Telegram handler
├── app.py                       # REST API (legacy, can remove)
├── llm_provider_v2.py          # Gemini integration
├── memory_service_v2.py        # Session persistence
├── telegram_security.py        # Webhook validation
├── rate_limiter.py            # Rate limiting logic
├── health_check.py            # Health endpoints
├── logger_config.py           # Logging setup
├── setup_telegram.py          # Webhook registration tool
├── Dockerfile                 # Container definition
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .dockerignore              # Docker ignore rules
├── start.bat                  # Quick start script
└── TELEGRAM_SETUP.md          # Setup guide
```

---

## 🎯 Next Steps

1. **Register Webhook** - Make bot accessible from Telegram
2. **Monitor Logs** - Watch real-time messages
3. **Test Thoroughly** - Ensure all features work
4. **Setup Backups** - Backup session database
5. **Deploy** - Push to production environment
6. **Monitor** - Watch for errors & performance

---

## 📊 Monitoring & Alerts

### Recommended Tools
- **Sentry** - Error tracking
- **Prometheus** - Metrics collection
- **Grafana** - Dashboards
- **Uptime Kuma** - Health monitoring

### Key Metrics
- Message latency
- Error rate
- Session count
- Memory usage
- CPU usage

---

## 🤝 Support

- 📖 Documentation: `TELEGRAM_SETUP.md`, `PRODUCTION_DEPLOYMENT.md`
- 🐛 Issues: Check logs and troubleshooting guides
- 📧 Backup: Save sessions regularly

---

## 📄 License

MIT License - See LICENSE.txt

---

## 🎉 Ready to Go!

Your NaMo ACC Telegram Bot is now production-ready!

**Start chatting:** Open Telegram and find `@Vipha_ACC_bot`

**Questions?** Check the documentation files or review server logs.

---

**Made with ❤️ for the NaMo Forbidden Archive community**
