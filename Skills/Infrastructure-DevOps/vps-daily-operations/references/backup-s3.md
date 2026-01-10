# S3 Backup Configuration with Restic

Complete guide for setting up encrypted, versioned backups to S3-compatible storage.

## Prerequisites

- S3-compatible storage (AWS S3, Backblaze B2, Wasabi, MinIO, etc.)
- Access credentials (Access Key ID + Secret Access Key)
- Restic installed: `sudo apt install restic`

## Initial Setup

### 1. Store Credentials Securely

```bash
# Create credentials file (root only)
sudo mkdir -p /root/.aws
sudo chmod 700 /root/.aws

sudo tee /root/.aws/credentials << 'EOF'
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
EOF

sudo chmod 600 /root/.aws/credentials

# Create Restic password file
sudo tee /root/.restic-password << 'EOF'
YOUR_STRONG_RESTIC_PASSWORD
EOF

sudo chmod 600 /root/.restic-password
```

### 2. Initialize Repository

```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=$(grep aws_access_key_id /root/.aws/credentials | cut -d= -f2 | tr -d ' ')
export AWS_SECRET_ACCESS_KEY=$(grep aws_secret_access_key /root/.aws/credentials | cut -d= -f2 | tr -d ' ')
export RESTIC_PASSWORD=$(cat /root/.restic-password)

# Initialize S3 repository
REPO="s3:s3.amazonaws.com/your-bucket-name/vps-backups"
restic init --repo $REPO

# For other providers:
# Backblaze B2: s3:s3.us-west-002.backblazeb2.com/your-bucket
# Wasabi: s3:s3.wasabisys.com/your-bucket
# MinIO: s3:minio.yourdomain.com/your-bucket
```

### 3. Create Backup Script

```bash
sudo tee /root/backup-to-s3.sh << 'EOF'
#!/bin/bash
set -e

# Load credentials
export AWS_ACCESS_KEY_ID=$(grep aws_access_key_id /root/.aws/credentials | cut -d= -f2 | tr -d ' ')
export AWS_SECRET_ACCESS_KEY=$(grep aws_secret_access_key /root/.aws/credentials | cut -d= -f2 | tr -d ' ')
export RESTIC_PASSWORD=$(cat /root/.restic-password)

# Configuration
REPO="s3:s3.amazonaws.com/your-bucket-name/vps-backups"
LOG_FILE="/var/log/backup-s3.log"

echo "====== S3 Backup $(date) ======" | tee -a "$LOG_FILE"

# Backup Dokploy database
echo "Backing up Dokploy database..." | tee -a "$LOG_FILE"
if docker ps | grep -q dokploy-db; then
    docker exec dokploy-db pg_dump -U dokploy | \
        restic backup --stdin --stdin-filename "dokploy-$(date +%Y%m%d).sql" --repo $REPO 2>&1 | tee -a "$LOG_FILE"
    echo "✓ Dokploy DB backed up" | tee -a "$LOG_FILE"
fi

# Backup Uptime Kuma data
echo "Backing up Uptime Kuma..." | tee -a "$LOG_FILE"
if [ -d ~/kuma-data ]; then
    restic backup ~/kuma-data --tag kuma --repo $REPO 2>&1 | tee -a "$LOG_FILE"
    echo "✓ Kuma data backed up" | tee -a "$LOG_FILE"
fi

# Backup Docker volumes (if needed)
# restic backup /var/lib/docker/volumes --tag docker-volumes --repo $REPO

# Prune old backups (keep last 30 daily, 12 weekly, 12 monthly)
echo "Pruning old backups..." | tee -a "$LOG_FILE"
restic forget --keep-daily 30 --keep-weekly 12 --keep-monthly 12 --prune --repo $REPO 2>&1 | tee -a "$LOG_FILE"

# Check repository integrity (once per week)
if [ $(date +%u) -eq 7 ]; then
    echo "Running repository check..." | tee -a "$LOG_FILE"
    restic check --repo $REPO 2>&1 | tee -a "$LOG_FILE"
fi

echo "====== Backup Complete ======" | tee -a "$LOG_FILE"
EOF

sudo chmod +x /root/backup-to-s3.sh
```

### 4. Schedule Backups

```bash
# Daily at 3 AM
(crontab -l 2>/dev/null; echo "0 3 * * * /root/backup-to-s3.sh") | crontab -

# Or use systemd timer (see vps-deployment-stack skill)
```

## Operations

### List Backups

```bash
export RESTIC_PASSWORD=$(cat /root/.restic-password)
REPO="s3:s3.amazonaws.com/your-bucket-name/vps-backups"

# List all snapshots
restic snapshots --repo $REPO

# List by tag
restic snapshots --tag kuma --repo $REPO
```

### Restore Data

**Restore Dokploy database:**
```bash
export RESTIC_PASSWORD=$(cat /root/.restic-password)
REPO="s3:s3.amazonaws.com/your-bucket-name/vps-backups"

# List available database backups
restic snapshots --repo $REPO | grep dokploy

# Restore specific snapshot
restic restore <snapshot-id> --target /tmp/restore --repo $REPO

# Apply to database
docker stop dokploy
cat /tmp/restore/dokploy-YYYYMMDD.sql | docker exec -i dokploy-db psql -U dokploy
docker start dokploy
```

**Restore Uptime Kuma:**
```bash
# Stop Kuma
docker compose -f ~/docker-compose.kuma.yml down

# Restore data
rm -rf ~/kuma-data
restic restore latest --target ~ --repo $REPO --include kuma-data

# Start Kuma
docker compose -f ~/docker-compose.kuma.yml up -d
```

### Verify Backups

```bash
# Check repository integrity
restic check --repo $REPO

# View backup statistics
restic stats --repo $REPO

# Compare snapshots
restic diff <snapshot1> <snapshot2> --repo $REPO
```

## Advanced Configuration

### Bandwidth Limiting

```bash
# Limit upload to 10 MB/s
restic backup ~/kuma-data --repo $REPO --limit-upload 10240
```

### Exclude Patterns

Create `/root/.restic-exclude`:
```
*.log
*.tmp
/kuma-data/cache/*
```

Use in backup:
```bash
restic backup ~/kuma-data --exclude-file=/root/.restic-exclude --repo $REPO
```

### Multiple Repositories

```bash
# Backup to multiple locations for redundancy
REPO1="s3:s3.amazonaws.com/bucket1/backups"
REPO2="s3:s3.wasabisys.com/bucket2/backups"

docker exec dokploy-db pg_dump -U dokploy | restic backup --stdin --repo $REPO1
docker exec dokploy-db pg_dump -U dokploy | restic backup --stdin --repo $REPO2
```

## Cost Optimization

### Storage Providers Comparison (as of 2024)

| Provider | Storage | Egress | Notes |
|----------|---------|--------|-------|
| Backblaze B2 | $0.005/GB | Free (1x stored) | Best value |
| Wasabi | $0.0059/GB | Free | 1TB minimum |
| AWS S3 | $0.023/GB | $0.09/GB | Expensive egress |
| S3 Glacier | $0.004/GB | $0.09/GB | Slow retrieval |

**Recommendation:** Backblaze B2 for most use cases.

### Retention Policy

Balance cost vs recovery needs:

```bash
# Aggressive (low cost)
restic forget --keep-daily 7 --keep-weekly 4 --prune

# Moderate (default)
restic forget --keep-daily 30 --keep-weekly 12 --keep-monthly 12 --prune

# Conservative (high cost)
restic forget --keep-daily 90 --keep-weekly 52 --keep-monthly 24 --keep-yearly 5 --prune
```

## Monitoring

### Check Backup Success

```bash
# View last backup log
tail -n 50 /var/log/backup-s3.log

# Check cron execution
grep backup-to-s3 /var/log/syslog

# Alert if no backup in 25 hours
LAST_BACKUP=$(restic snapshots --json --repo $REPO | jq -r '.[0].time')
if [ $(( $(date +%s) - $(date -d "$LAST_BACKUP" +%s) )) -gt 90000 ]; then
    echo "WARNING: No backup in 25 hours"
fi
```

### Add to Uptime Kuma

Create a custom monitor:
1. Monitor Type: HTTP(s) - Keyword
2. URL: Your backup log endpoint (or use script status)
3. Keyword: "Backup Complete"
4. Interval: Daily + 6 hours

## Troubleshooting

### Authentication Failed
```bash
# Verify credentials
aws s3 ls s3://your-bucket --profile default

# Test Restic connection
restic snapshots --repo $REPO
```

### Slow Uploads
```bash
# Check network speed
speedtest-cli

# Use closer S3 region
# Change s3.amazonaws.com to s3.us-west-2.amazonaws.com

# Enable compression (already default in Restic)
```

### Repository Locked
```bash
# If backup interrupted, remove stale lock
restic unlock --repo $REPO
```

### Out of Space
```bash
# Check repository size
restic stats --repo $REPO

# Aggressive prune
restic forget --keep-last 5 --prune --repo $REPO
```

## Security Best Practices

- ✓ Use strong RESTIC_PASSWORD (32+ chars, random)
- ✓ Rotate access keys quarterly
- ✓ Enable S3 bucket versioning (extra protection)
- ✓ Restrict bucket policy to backup IP only
- ✓ Use S3 bucket encryption (AES-256)
- ✓ Test restores monthly
- ✓ Store credentials file with 600 permissions
- ✗ Never commit credentials to Git
- ✗ Never use same password for repository and S3

## Recovery Drill

Schedule quarterly disaster recovery tests:

1. **Simulate failure:** Stop all services
2. **Restore from backup:** Use latest snapshot
3. **Verify functionality:** Check all services work
4. **Document time:** Measure MTTR (Mean Time To Recovery)
5. **Update runbook:** Note any issues found

Goal: Complete recovery in <30 minutes.
