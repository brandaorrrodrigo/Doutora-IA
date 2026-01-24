#!/bin/bash

# ============================================
# DOUTORA IA - PRODUCTION DEPLOYMENT SCRIPT
# ============================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_USER=${DEPLOY_USER:-"deploy"}
DEPLOY_PATH=${DEPLOY_PATH:-"/var/www/doutora-ia"}
DOMAIN=${DOMAIN:-"doutora-ia.com"}
EMAIL=${EMAIL:-"admin@doutora-ia.com"}

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}DOUTORA IA - Production Deploy${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root. Consider using a dedicated deploy user.${NC}"
fi

# Function to print step
print_step() {
    echo -e "${GREEN}▶ $1${NC}"
}

# Function to print error and exit
error_exit() {
    echo -e "${RED}✗ Error: $1${NC}" >&2
    exit 1
}

# ============================================
# STEP 1: System Prerequisites
# ============================================
print_step "1/8 Checking system prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    error_exit "Docker is not installed. Please install Docker first."
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    error_exit "Docker Compose is not installed. Please install Docker Compose first."
fi

# Check if Git is installed
if ! command -v git &> /dev/null; then
    error_exit "Git is not installed. Please install Git first."
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# ============================================
# STEP 2: Clone or Update Repository
# ============================================
print_step "2/8 Setting up repository..."

if [ ! -d "$DEPLOY_PATH" ]; then
    echo "Cloning repository..."
    git clone https://github.com/your-org/doutora-ia.git "$DEPLOY_PATH"
    cd "$DEPLOY_PATH"
else
    echo "Updating repository..."
    cd "$DEPLOY_PATH"
    git fetch origin
    git pull origin main
fi

echo -e "${GREEN}✓ Repository ready${NC}"
echo ""

# ============================================
# STEP 3: Environment Configuration
# ============================================
print_step "3/8 Configuring environment variables..."

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env

    echo -e "${YELLOW}IMPORTANT: Edit .env file with your production credentials!${NC}"
    echo "Required variables:"
    echo "  - OPENAI_API_KEY"
    echo "  - PG_PASSWORD"
    echo "  - SECRET_KEY"
    echo "  - MERCADO_PAGO_ACCESS_TOKEN (if using payments)"
    echo ""
    read -p "Press Enter after editing .env file..."
else
    echo ".env file already exists"
fi

# Generate SECRET_KEY if not set
if ! grep -q "SECRET_KEY=" .env || grep -q "SECRET_KEY=change_this" .env; then
    echo "Generating SECRET_KEY..."
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
fi

echo -e "${GREEN}✓ Environment configured${NC}"
echo ""

# ============================================
# STEP 4: SSL Certificates (Let's Encrypt)
# ============================================
print_step "4/8 Setting up SSL certificates..."

mkdir -p certbot/conf certbot/www

if [ ! -f "certbot/conf/live/$DOMAIN/fullchain.pem" ]; then
    echo "Obtaining SSL certificate from Let's Encrypt..."

    # Start nginx temporarily for cert validation
    docker-compose -f docker-compose.prod.yml up -d nginx

    # Get certificate
    docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        -d "api.$DOMAIN"

    # Restart nginx with SSL
    docker-compose -f docker-compose.prod.yml restart nginx
else
    echo "SSL certificates already exist"
fi

echo -e "${GREEN}✓ SSL configured${NC}"
echo ""

# ============================================
# STEP 5: Build Docker Images
# ============================================
print_step "5/8 Building Docker images..."

docker-compose -f docker-compose.prod.yml build --no-cache

echo -e "${GREEN}✓ Images built${NC}"
echo ""

# ============================================
# STEP 6: Database Setup
# ============================================
print_step "6/8 Setting up database..."

# Start database
docker-compose -f docker-compose.prod.yml up -d db qdrant

# Wait for database
echo "Waiting for database to be ready..."
sleep 10

# Run migrations
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# Seed initial data (optional)
read -p "Seed database with initial data? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.prod.yml run --rm api python -c "
from main import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.post('/seed')
print('Seed result:', response.json())
"
fi

echo -e "${GREEN}✓ Database ready${NC}"
echo ""

# ============================================
# STEP 7: Start All Services
# ============================================
print_step "7/8 Starting all services..."

docker-compose -f docker-compose.prod.yml up -d

# Wait for services
echo "Waiting for services to start..."
sleep 20

# Health check
echo "Running health checks..."
MAX_RETRIES=30
RETRY=0

until curl -f http://localhost/health &> /dev/null || [ $RETRY -eq $MAX_RETRIES ]; do
    echo "Waiting for API... ($RETRY/$MAX_RETRIES)"
    RETRY=$((RETRY+1))
    sleep 2
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    error_exit "Health check failed. Services may not be running correctly."
fi

echo -e "${GREEN}✓ All services running${NC}"
echo ""

# ============================================
# STEP 8: Final Checks and Info
# ============================================
print_step "8/8 Final checks..."

# Show running containers
echo "Running containers:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""
echo "Access your application at:"
echo -e "  ${BLUE}Web App:${NC} https://$DOMAIN"
echo -e "  ${BLUE}API:${NC}     https://api.$DOMAIN"
echo -e "  ${BLUE}Health:${NC}  https://api.$DOMAIN/health"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose -f docker-compose.prod.yml logs -f"
echo "  Restart:      docker-compose -f docker-compose.prod.yml restart"
echo "  Stop:         docker-compose -f docker-compose.prod.yml down"
echo "  Update:       git pull && docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo -e "${YELLOW}Don't forget to:${NC}"
echo "  1. Configure DNS to point to this server"
echo "  2. Setup automated backups (see scripts/backup.sh)"
echo "  3. Configure monitoring and alerts"
echo "  4. Review security settings"
echo ""
