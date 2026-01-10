#!/bin/bash
set -e

BACKUP_DIR="/root/backups"
mkdir -p "$BACKUP_DIR"

echo "====== Weekly Maintenance ======"
date

# 1. System updates
echo "=== Updating packages ==="
apt update && apt upgrade -y
apt autoremove -y

# 2. Clean Docker cache
echo "=== Cleaning Docker ==="
docker system prune -f
docker image prune -a -f --filter "until=168h"  # Remove images >7 days old

# 3. Backup Dokploy database
echo "=== Backing up Dokploy DB ==="
if docker ps | grep -q dokploy-db; then
    docker exec dokploy-db pg_dump -U dokploy > "$BACKUP_DIR/dokploy-$(date +%Y%m%d).sql"
    echo "✓ Database backed up to $BACKUP_DIR/dokploy-$(date +%Y%m%d).sql"
else
    echo "⚠️  Dokploy database container not found"
fi

# 4. Backup Uptime Kuma data
echo "=== Backing up Kuma ==="
if [ -d ~/kuma-data ]; then
    tar -czf "$BACKUP_DIR/kuma-$(date +%Y%m%d).tar.gz" ~/kuma-data
    echo "✓ Kuma data backed up to $BACKUP_DIR/kuma-$(date +%Y%m%d).tar.gz"
else
    echo "⚠️  Kuma data directory not found"
fi

# 5. Clean old backups (>30 days)
echo "=== Cleaning old backups ==="
DELETED_SQL=$(find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete -print | wc -l)
DELETED_TAR=$(find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete -print | wc -l)
echo "Deleted $DELETED_SQL old SQL backups and $DELETED_TAR old tarballs"

# 6. Disk usage report
echo "=== Disk Usage Report ==="
echo "Docker:"
docker system df
echo -e "\nSystem:"
df -h / | grep -v Filesystem

# 7. Check for container restarts (sign of instability)
echo "=== Container Restart Count ==="
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -i restart || echo "No containers restarting"

echo "====== Maintenance Complete ======"
echo "Backup location: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"
