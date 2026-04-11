#!/bin/bash
# =============================================================================
# UIG Property Acquisition Pipeline — VPS Deploy Script
# Domain: lpi.directory
# Run this on your VPS as root or sudo user
# Usage: bash deploy.sh
# =============================================================================

set -euo pipefail

DOMAIN="lpi.directory"
EMAIL="admin@uigllc.org"          # Let's Encrypt notification email
REPO="https://github.com/navigatorxm/uig-llc.git"
DEPLOY_DIR="/opt/uig-llc"

echo "============================================="
echo "  UIG LPI Pipeline — Production Deployment"
echo "  Domain: $DOMAIN"
echo "============================================="

# ---------------------------------------------------------------
# 1. Install system dependencies
# ---------------------------------------------------------------
echo "[1/8] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq \
    git \
    curl \
    docker.io \
    docker-compose-plugin \
    ufw \
    fail2ban

# Start Docker
systemctl enable --now docker
usermod -aG docker "$USER" 2>/dev/null || true

# ---------------------------------------------------------------
# 2. Firewall
# ---------------------------------------------------------------
echo "[2/8] Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo "Firewall configured."

# ---------------------------------------------------------------
# 3. Clone / pull the repo
# ---------------------------------------------------------------
echo "[3/8] Pulling latest code..."
if [ -d "$DEPLOY_DIR/.git" ]; then
    cd "$DEPLOY_DIR"
    git pull origin main
else
    git clone "$REPO" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

# ---------------------------------------------------------------
# 4. Confirm .env exists (do NOT overwrite if already there)
# ---------------------------------------------------------------
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    echo "ERROR: .env not found at $DEPLOY_DIR/.env"
    echo "Please copy your .env to the VPS first:"
    echo "  scp .env root@<vps-ip>:$DEPLOY_DIR/.env"
    exit 1
fi
echo "[4/8] .env found — OK"

# ---------------------------------------------------------------
# 5. Bootstrap Let's Encrypt (first-time SSL only)
# ---------------------------------------------------------------
echo "[5/8] Setting up SSL certificate..."

# Use a temporary HTTP-only nginx to complete ACME challenge
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "  No existing cert — running Certbot standalone to issue initial cert..."

    # Temporarily use the bootstrap nginx config
    docker run --rm -p 80:80 \
        -v "/etc/letsencrypt:/etc/letsencrypt" \
        -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
        certbot/certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" \
        -d "www.$DOMAIN"

    echo "  SSL certificate issued successfully!"
else
    echo "  Existing cert found — skipping initial issue."
fi

# ---------------------------------------------------------------
# 6. Build and start all containers
# ---------------------------------------------------------------
echo "[6/8] Building Docker images (this may take a few minutes)..."
cd "$DEPLOY_DIR"
docker compose pull --quiet 2>/dev/null || true
docker compose up --build -d

echo "  Waiting for services to be healthy..."
sleep 20

# ---------------------------------------------------------------
# 7. Health check
# ---------------------------------------------------------------
echo "[7/8] Running health check..."
for i in $(seq 1 10); do
    if curl -sf "http://localhost/health" > /dev/null 2>&1; then
        echo "  ✅ Backend is responding!"
        break
    fi
    echo "  Waiting... ($i/10)"
    sleep 5
done

HTTPS_STATUS=$(curl -sk -o /dev/null -w "%{http_code}" "https://$DOMAIN/health" 2>/dev/null || echo "000")
if [ "$HTTPS_STATUS" = "200" ]; then
    echo "  ✅ HTTPS is working! (https://$DOMAIN/health → 200)"
else
    echo "  ⚠️  HTTPS returned $HTTPS_STATUS — DNS may not have propagated yet."
    echo "     Try: curl https://$DOMAIN/health"
fi

# ---------------------------------------------------------------
# 8. Setup automatic DB backup cron (daily at 2am UTC)
# ---------------------------------------------------------------
echo "[8/8] Configuring daily PostgreSQL backup cron..."
BACKUP_SCRIPT="/opt/uig-backup.sh"
cat > "$BACKUP_SCRIPT" << 'BACKUP_EOF'
#!/bin/bash
DEPLOY_DIR="/opt/uig-llc"
BACKUP_DIR="/opt/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"
cd "$DEPLOY_DIR"
source .env
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | \
    gzip > "$BACKUP_DIR/uig_pipeline_$DATE.sql.gz"
# Keep only last 14 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +14 -delete
echo "[$(date)] Backup completed: uig_pipeline_$DATE.sql.gz"
BACKUP_EOF
chmod +x "$BACKUP_SCRIPT"

# Add to crontab if not already there
(crontab -l 2>/dev/null | grep -v "uig-backup" ; echo "0 2 * * * $BACKUP_SCRIPT >> /var/log/uig-backup.log 2>&1") | crontab -
echo "  Daily backup cron set at 02:00 UTC → /opt/backups/postgres/"

# ---------------------------------------------------------------
# Done!
# ---------------------------------------------------------------
echo ""
echo "============================================="
echo "  🚀 Deployment Complete!"
echo "============================================="
echo "  Dashboard:  https://$DOMAIN/dashboard"
echo "  API docs:   https://$DOMAIN/api/docs"
echo "  Health:     https://$DOMAIN/health"
echo ""
echo "  Next steps:"
echo "  1. Verify DNS: dig +short lpi.directory — should show your VPS IP"
echo "  2. Login at https://lpi.directory/login"
echo "     Email: admin@uigllc.org | Password: UIG@admin2026"
echo "  3. IMMEDIATELY change the admin password!"
echo "  4. Add CashFree credentials in Settings (dashboard)"
echo "  5. Add your API keys (Twilio, SendGrid, HubSpot, etc.)"
echo "============================================="
