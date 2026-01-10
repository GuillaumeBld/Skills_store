#!/bin/bash
set -e

LOG_FILE="/var/log/vps-daily-check.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "====== VPS Health Check ======"
echo "Date: $(date)"
echo "Hostname: $(hostname)"

# 1. Container status
echo -e "\n=== Docker Containers ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.State}}"

# 2. Disk usage
echo -e "\n=== Disk Usage ==="
df -h / | grep -v Filesystem
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
    echo "⚠️  WARNING: Disk usage >85%"
fi

# 3. Memory usage
echo -e "\n=== Memory Usage ==="
free -h | grep Mem

# 4. Dokploy health (update domain)
echo -e "\n=== Dokploy API ==="
DOKPLOY_DOMAIN="deploy.yourdomain.com"  # UPDATE THIS
curl -sf https://$DOKPLOY_DOMAIN/api/health && echo "✓ OK" || echo "✗ FAILED"

# 5. Certificate expiry
echo -e "\n=== TLS Certificate ==="
echo | openssl s_client -connect $DOKPLOY_DOMAIN:443 -servername $DOKPLOY_DOMAIN 2>/dev/null | openssl x509 -noout -dates | grep "notAfter"

# 6. Failed systemd services
echo -e "\n=== Failed Services ==="
systemctl --failed

# 7. Docker system info
echo -e "\n=== Docker System ==="
docker system df

echo -e "\n====== Check Complete ======\n"
