# NaMo ACC Bot - Production Deployment Guide

## 🚀 Deployment Options

### Option 1: Railway (Recommended - Easiest)
```bash
# 1. Push to GitHub
git add .
git commit -m "NaMo ACC Bot production ready"
git push origin main

# 2. Connect Railway to GitHub repo
# https://railway.app/dashboard
# - New Project → GitHub Repo
# - Configure variables
# - Deploy
```

### Option 2: Render
```bash
# 1. Create render.yaml
version: 1
services:
  - type: web
    name: namo-acc
    runtime: docker
    plan: paid
    dockerfilePath: ./projects-NaMo-Forbidden-Archive/Dockerfile
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: GEMINI_API_KEY
        sync: false

# 2. Push to GitHub and connect Render
```

### Option 3: AWS Lambda + API Gateway
```bash
# Install serverless framework
npm install -g serverless

# Deploy
serverless deploy --region us-east-1
```

### Option 4: Docker Compose on VPS
```bash
# SSH to your server
ssh user@your-domain.com

# Clone repo
git clone https://github.com/your-username/NaMo_Forbidden_Archive.git
cd NaMo_Forbidden_Archive

# Create .env with secrets
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_token_here
GEMINI_API_KEY=your_key_here
EOF

# Run docker compose
docker compose up -d

# Setup reverse proxy (see below)
```

---

## 🔒 Environment Variables (Required)

```env
# Core
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
GEMINI_API_KEY=your_google_ai_key
PORT=8080

# Optional but recommended
DEBUG=false
LOG_DIR=./logs
USE_GCS=false
GCS_BUCKET_NAME=
QDRANT_HOST=qdrant
REDIS_URL=redis://localhost:6379
```

---

## 🌐 Nginx Reverse Proxy Setup

Create `/etc/nginx/sites-available/namo-acc`:

```nginx
upstream namo_acc_backend {
    server localhost:8080;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://namo_acc_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://namo_acc_backend;
        access_log off;
    }
}
```

Enable it:
```bash
sudo ln -s /etc/nginx/sites-available/namo-acc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔐 SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
# Auto-renew via cron (automatic with certbot)
```

---

## 📊 Monitor & Logs

```bash
# View logs
docker logs -f namo-acc

# Follow specific log file
tail -f ./logs/acc_bot_*.log

# Real-time monitoring
docker stats namo-acc
```

---

## 🔄 Auto-restart on Reboot

### Docker Compose
```bash
# Add to docker-compose.yml
services:
  telegram-bot:
    restart: always
```

### Systemd Service
Create `/etc/systemd/system/namo-acc.service`:

```ini
[Unit]
Description=NaMo ACC Bot
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=always
RestartSec=10
User=root
WorkingDirectory=/home/user/NaMo_Forbidden_Archive
ExecStart=/usr/bin/docker compose up
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable namo-acc
sudo systemctl start namo-acc
```

---

## 📈 Scaling for High Traffic

### 1. Use Load Balancer
```nginx
upstream namo_acc_cluster {
    server localhost:8080;
    server localhost:8081;
    server localhost:8082;
}
```

### 2. Use Redis for Sessions
```python
# In memory_service_v2.py
USE_REDIS = True
REDIS_URL = "redis://redis-cluster:6379"
```

### 3. Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: namo-acc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: namo-acc
  template:
    metadata:
      labels:
        app: namo-acc
    spec:
      containers:
      - name: namo-acc
        image: ghcr.io/your-username/namo-acc:latest
        ports:
        - containerPort: 8080
        env:
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: namo-secrets
              key: telegram-token
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: namo-secrets
              key: gemini-key
        livenessProbe:
          httpGet:
            path: /live
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

Deploy:
```bash
kubectl apply -f namo-acc-deployment.yaml
```

---

## 🚨 Troubleshooting

### Bot not receiving messages
```bash
# Check webhook
curl https://api.telegram.org/bot{TOKEN}/getWebhookInfo

# Re-register webhook
python setup_telegram.py --webhook-url https://your-domain.com/webhook/telegram
```

### High latency
- Check Gemini API quota
- Monitor Redis/Database performance
- Review rate limiting settings

### Memory leaks
```bash
# Monitor memory
docker stats namo-acc

# Check for circular references in memory_service
```

---

## 📋 Checklist

- [ ] Environment variables set in CI/CD
- [ ] Database backups configured
- [ ] Logging to file enabled
- [ ] SSL certificate installed
- [ ] Webhook registered with Telegram
- [ ] Rate limiting active
- [ ] Health checks monitoring
- [ ] CI/CD pipeline working
- [ ] Backup strategy in place
- [ ] Monitoring/alerting configured

---

**Deployment complete! 🎉**
