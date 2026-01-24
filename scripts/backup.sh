#!/bin/bash

# ============================================
# DOUTORA IA - BACKUP SCRIPT
# ============================================

set -e

# Configuration
BACKUP_DIR=${BACKUP_DIR:-"/var/backups/doutora-ia"}
DEPLOY_PATH=${DEPLOY_PATH:-"/var/www/doutora-ia"}
RETENTION_DAYS=${RETENTION_DAYS:-30}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "================================"
echo "DOUTORA IA - Backup Script"
echo "================================"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

cd "$DEPLOY_PATH"

# ============================================
# 1. Backup PostgreSQL Database
# ============================================
echo -e "${GREEN}1/4 Backing up PostgreSQL...${NC}"

DB_BACKUP_FILE="$BACKUP_DIR/postgres_$TIMESTAMP.sql.gz"

docker-compose -f docker-compose.prod.yml exec -T db pg_dumpall -U postgres | gzip > "$DB_BACKUP_FILE"

echo "✓ Database backed up to $DB_BACKUP_FILE"
echo ""

# ============================================
# 2. Backup Qdrant Vector Database
# ============================================
echo -e "${GREEN}2/4 Backing up Qdrant...${NC}"

QDRANT_BACKUP_FILE="$BACKUP_DIR/qdrant_$TIMESTAMP.tar.gz"

# Create Qdrant snapshot
docker-compose -f docker-compose.prod.yml exec -T qdrant \
    curl -X POST "http://localhost:6333/snapshots" \
    -H "Content-Type: application/json" \
    -d '{"snapshot_name": "backup_'$TIMESTAMP'"}'

# Copy snapshot
docker cp $(docker-compose -f docker-compose.prod.yml ps -q qdrant):/qdrant/snapshots "$BACKUP_DIR/qdrant_temp"
tar -czf "$QDRANT_BACKUP_FILE" -C "$BACKUP_DIR" qdrant_temp
rm -rf "$BACKUP_DIR/qdrant_temp"

echo "✓ Qdrant backed up to $QDRANT_BACKUP_FILE"
echo ""

# ============================================
# 3. Backup Static Files and Uploads
# ============================================
echo -e "${GREEN}3/4 Backing up static files...${NC}"

STATIC_BACKUP_FILE="$BACKUP_DIR/static_$TIMESTAMP.tar.gz"

tar -czf "$STATIC_BACKUP_FILE" \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='*.log' \
    api/static/ \
    api/templates/ \
    web-app/public/ \
    2>/dev/null || true

echo "✓ Static files backed up to $STATIC_BACKUP_FILE"
echo ""

# ============================================
# 4. Backup Configuration Files
# ============================================
echo -e "${GREEN}4/4 Backing up configuration...${NC}"

CONFIG_BACKUP_FILE="$BACKUP_DIR/config_$TIMESTAMP.tar.gz"

tar -czf "$CONFIG_BACKUP_FILE" \
    .env \
    docker-compose.prod.yml \
    nginx/doutora-ia.conf \
    certbot/conf/ \
    2>/dev/null || true

echo "✓ Configuration backed up to $CONFIG_BACKUP_FILE"
echo ""

# ============================================
# Cleanup Old Backups
# ============================================
echo -e "${GREEN}Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"

find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "✓ Old backups cleaned"
echo ""

# ============================================
# Summary
# ============================================
echo "================================"
echo "Backup Complete!"
echo "================================"
echo ""
echo "Backup files created:"
ls -lh "$BACKUP_DIR"/*"$TIMESTAMP"* | awk '{print "  " $9, "(" $5 ")"}'
echo ""
echo "Total backup size:"
du -sh "$BACKUP_DIR" | awk '{print "  " $1}'
echo ""

# Optional: Upload to S3 or remote storage
if [ -n "$AWS_S3_BUCKET" ]; then
    echo "Uploading to S3..."
    aws s3 cp "$BACKUP_DIR/" "s3://$AWS_S3_BUCKET/backups/doutora-ia/" \
        --recursive \
        --exclude "*" \
        --include "*$TIMESTAMP*"
    echo "✓ Uploaded to S3"
fi

echo "Backup completed successfully!"
