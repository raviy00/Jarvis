#!/bin/bash
# ===================================================
# Jarvis AI - Oracle Cloud Free Tier Setup Script
# Run this on your Oracle Cloud VM (Ubuntu 22.04)
# ===================================================

set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      🤖 Jarvis AI - Cloud Setup          ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. Update system ────────────────────────────
echo "▶ Updating system..."
sudo apt-get update -y && sudo apt-get upgrade -y

# ── 2. Install Docker ───────────────────────────
echo "▶ Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# ── 3. Install Docker Compose ───────────────────
echo "▶ Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# ── 4. Open firewall for web dashboard ──────────
echo "▶ Configuring firewall..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5000 -j ACCEPT
sudo netfilter-persistent save 2>/dev/null || true
echo "✅ Port 5000 opened"

# ── 5. Clone Jarvis repo ─────────────────────────
echo "▶ Cloning Jarvis..."
if [ ! -d "Jarvis" ]; then
    git clone https://github.com/raviy00/Jarvis.git
    echo "✅ Jarvis cloned"
else
    echo "✅ Jarvis already cloned, pulling latest..."
    cd Jarvis && git pull && cd ..
fi
cd Jarvis

# ── 6. Build and start ──────────────────────────
echo "▶ Building Docker image (this may take 5-10 mins)..."
docker-compose build

echo "▶ Starting Jarvis..."
docker-compose up -d

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅ Jarvis is LIVE!                      ║"
echo "║  Dashboard: http://$(curl -s ifconfig.me):5000  ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f     → View live logs"
echo "  docker-compose restart     → Restart Jarvis"
echo "  docker-compose down        → Stop Jarvis"
