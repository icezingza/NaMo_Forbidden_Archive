#!/usr/bin/env bash
# setup_oracle_vps.sh - Automated 24/7 Setup for Oracle Cloud Always Free ARM VPS
# NRE v6.0.0 Sovereign Architecture

set -e

echo "🚀 Starting NaMo Sovereign Engine Setup on Oracle Cloud VPS..."

# 1. Update system & install dependencies
sudo apt-get update && sudo apt-get install -y \
    curl git python3 python3-pip python3-venv ffmpeg docker.io docker-compose-plugin

sudo systemctl enable --now docker
sudo usermod -aG docker $USER

# 2. Setup Python Virtual Environment
echo "📦 Setting up Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt || pip install fastapi uvicorn httpx pydantic requests python-dotenv edge-tts neo4j pytelegrambotapi

# 3. Setup Systemd Service for 24/7 Auto-restart
echo "⚙️ Creating Systemd Service (namo-engine.service)..."
cat <<EOF | sudo tee /etc/systemd/system/namo-engine.service
[Unit]
Description=NaMo Sovereign Engine & Telegram Bot (24/7 Daemon)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8085
Restart=always
RestartSec=5
Environment=PATH=$(pwd)/venv/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/systemd/system/namo-bot.service
[Unit]
Description=NaMo Telegram Bot Daemon
After=namo-engine.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python telegram_bot.py
Restart=always
RestartSec=5
Environment=PATH=$(pwd)/venv/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

# 4. Enable and Start Services
sudo systemctl daemon-reload
sudo systemctl enable --now namo-engine.service
sudo systemctl enable --now namo-bot.service

# 5. Setup Local Cron Job for Midnight Dream Loop & 12-Hour Idle Ping
echo "📅 Setting up Local Crontab for Memory Consolidation & Idle Pings..."
(crontab -l 2>/dev/null | grep -v "v1/system"; echo "0 0 * * * curl -X POST http://127.0.0.1:8085/v1/system/consolidate-memory > /dev/null 2>&1") | crontab -
(crontab -l 2>/dev/null | grep -v "ping-idle"; echo "0 */12 * * * curl -X POST http://127.0.0.1:8085/v1/system/ping-idle > /dev/null 2>&1") | crontab -

echo "🎉 Oracle Cloud VPS Setup Complete!"
echo " NaMo Engine & Telegram Bot are running 24/7 in the background!"
echo " Check status with: sudo systemctl status namo-engine namo-bot"
