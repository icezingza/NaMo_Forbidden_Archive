#!/bin/bash
# SSL Certificate Setup & Automation for NaMo ACC Bot
# Uses Let's Encrypt for automatic renewal

set -e

DOMAIN="your-domain.com"
EMAIL="your-email@example.com"
CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"
SSL_DIR="./ssl"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🔐 NaMo ACC Bot - SSL Certificate Setup${NC}"
echo "========================================"

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo -e "${RED}❌ certbot not found. Installing...${NC}"
    if command -v apt &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y certbot python3-certbot-nginx
    elif command -v yum &> /dev/null; then
        sudo yum install -y certbot python3-certbot-nginx
    else
        echo -e "${RED}❌ Package manager not found. Please install certbot manually.${NC}"
        exit 1
    fi
fi

# Prompt for configuration
read -p "Enter domain name [$DOMAIN]: " domain_input
if [ -n "$domain_input" ]; then
    DOMAIN="$domain_input"
fi

read -p "Enter email address [$EMAIL]: " email_input
if [ -n "$email_input" ]; then
    EMAIL="$email_input"
fi

echo -e "\n${YELLOW}📝 Configuration:${NC}"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo "Cert Dir: $CERT_DIR"

# Create SSL directory
mkdir -p "${SSL_DIR}"

# Function: Obtain certificate
obtain_cert() {
    echo -e "\n${YELLOW}🔑 Obtaining SSL certificate...${NC}"
    
    # Using standalone mode for initial setup
    sudo certbot certonly \
        --standalone \
        --agree-tos \
        --non-interactive \
        --email "${EMAIL}" \
        -d "${DOMAIN}" \
        -d "www.${DOMAIN}"
    
    if [ -f "${CERT_DIR}/fullchain.pem" ]; then
        echo -e "${GREEN}✅ Certificate obtained successfully${NC}"
        
        # Copy to local directory
        sudo cp "${CERT_DIR}/fullchain.pem" "${SSL_DIR}/cert.pem"
        sudo cp "${CERT_DIR}/privkey.pem" "${SSL_DIR}/key.pem"
        sudo chown $(whoami):$(whoami) "${SSL_DIR}"/*.pem
        
        echo -e "${GREEN}✅ Certificates copied to ${SSL_DIR}${NC}"
    else
        echo -e "${RED}❌ Failed to obtain certificate${NC}"
        exit 1
    fi
}

# Function: Setup auto-renewal
setup_renewal() {
    echo -e "\n${YELLOW}⏰ Setting up auto-renewal...${NC}"
    
    # Create renewal script
    cat > /tmp/renew-ssl.sh << 'EOF'
#!/bin/bash
# Renew SSL certificate and reload services

DOMAIN="$1"
EMAIL="$2"
SSL_DIR="$3"
CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"

# Renew certificate
certbot renew --quiet

# Copy new certificates
cp "${CERT_DIR}/fullchain.pem" "${SSL_DIR}/cert.pem"
cp "${CERT_DIR}/privkey.pem" "${SSL_DIR}/key.pem"

# Reload services
if command -v systemctl &> /dev/null; then
    systemctl reload nginx || true
fi

# Notify
echo "[$(date)] SSL certificate renewed for ${DOMAIN}" >> /var/log/ssl-renewal.log
EOF
    
    chmod +x /tmp/renew-ssl.sh
    
    # Add cron job for renewal (runs daily at 2 AM)
    (crontab -l 2>/dev/null | grep -v "/tmp/renew-ssl.sh"; echo "0 2 * * * /tmp/renew-ssl.sh ${DOMAIN} ${EMAIL} ${SSL_DIR}") | crontab -
    
    echo -e "${GREEN}✅ Auto-renewal cron job added${NC}"
}

# Function: Generate self-signed cert (for testing)
generate_self_signed() {
    echo -e "\n${YELLOW}🧪 Generating self-signed certificate for testing...${NC}"
    
    openssl req -x509 -newkey rsa:4096 \
        -keyout "${SSL_DIR}/key.pem" \
        -out "${SSL_DIR}/cert.pem" \
        -days 365 -nodes \
        -subj "/CN=${DOMAIN}/O=NaMo ACC Bot/C=US"
    
    echo -e "${GREEN}✅ Self-signed certificate generated (valid for 365 days)${NC}"
}

# Function: Check certificate validity
check_cert() {
    echo -e "\n${YELLOW}🔍 Checking certificate validity...${NC}"
    
    if [ -f "${SSL_DIR}/cert.pem" ]; then
        openssl x509 -in "${SSL_DIR}/cert.pem" -text -noout | grep -A 2 "Validity"
    else
        echo -e "${RED}❌ Certificate not found${NC}"
    fi
}

# Main menu
echo -e "\n${YELLOW}Select option:${NC}"
echo "1. Obtain Let's Encrypt certificate"
echo "2. Generate self-signed certificate (testing)"
echo "3. Check certificate validity"
echo "4. Setup auto-renewal"
echo "5. Full setup (1+4)"

read -p "Choose [1-5]: " choice

case $choice in
    1) obtain_cert ;;
    2) generate_self_signed ;;
    3) check_cert ;;
    4) setup_renewal ;;
    5) obtain_cert && setup_renewal ;;
    *) echo "Invalid choice" && exit 1 ;;
esac

echo -e "\n${GREEN}✅ SSL setup complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Update nginx.conf with certificate paths:"
echo "   ssl_certificate /path/to/ssl/cert.pem;"
echo "   ssl_certificate_key /path/to/ssl/key.pem;"
echo "2. Restart nginx:"
echo "   sudo systemctl restart nginx"
echo "3. Test SSL:"
echo "   curl -I https://${DOMAIN}"
