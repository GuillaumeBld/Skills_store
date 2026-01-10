---
name: vps-daily-operations
description: VPS operational procedures including daily health checks, weekly maintenance, monitoring configuration, incident response, security hardening, and backup strategies. Use when setting up automated monitoring for Dokploy/Docker infrastructure, implementing SSH hardening with Fail2Ban, configuring backup routines, responding to incidents (disk full, OOM, compromised containers), or establishing operational runbooks. Includes ready-to-use bash scripts for automation via cron or systemd timers.
---

# VPS Daily Operations

Operational runbooks, automation scripts, and incident response procedures for production VPS management.

## Prerequisites

- vps-deployment-stack skill completed (Dokploy + Traefik + Docker + Kuma deployed)
- SSH access with sudo privileges
- Basic familiarity with cron or systemd timers

## Quick Start: Automate Daily Operations

### 1. Setup Daily Health Checks (10 min)

See `scripts/daily-vps-check.sh` for the complete script.

Install and schedule:
```bash
# Copy script from skill
sudo cp scripts/daily-vps-check.sh /root/
sudo chmod +x /root/daily-vps-check.sh

# Test manually
sudo /root/daily-vps-check.sh

# Schedule with cron (9 AM daily)
(crontab -l 2>/dev/null; echo "0 9 * * * /root/daily-vps-check.sh") | crontab -
```

The script checks:
- Container status (docker ps)
- Disk usage (warns if >85%)
- Memory usage
- Dokploy API health
- TLS certificate expiry
- Failed systemd services

### 2. Setup Weekly Maintenance (10 min)

See `scripts/weekly-maintenance.sh` for the complete script.

Install and schedule:
```bash
# Copy and setup
sudo cp scripts/weekly-maintenance.sh /root/
sudo chmod +x /root/weekly-maintenance.sh

# Schedule (Sundays at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * 0 /root/weekly-maintenance.sh") | crontab -
```

The script performs:
- System package updates
- Docker cache cleanup
- Dokploy database backup
- Uptime Kuma data backup
- Old backup removal (>30 days)

### 3. Harden SSH (5 min)

**CRITICAL: Test in separate SSH session before disconnecting!**

```bash
# Backup config
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# Edit config
sudo nano /etc/ssh/sshd_config
```

Change:
```
Port 2222                      # Non-standard port
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
```

Apply:
```bash
sudo sshd -t  # Test config
sudo systemctl restart sshd
```

**Test in NEW terminal before disconnecting:**
```bash
ssh -p 2222 user@YOUR_VPS_IP
```

### 4. Install Fail2Ban (5 min)

```bash
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

Configure:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
backend = systemd
```

Start:
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo fail2ban-client status sshd
```

### 5. Configure Uptime Kuma (10 min)

In Uptime Kuma UI (https://status.yourdomain.com):

**Add monitors:**
- Dokploy: HTTPS → deploy.yourdomain.com → 60s interval
- VPS SSH: TCP → YOUR_IP:2222 → 300s interval
- Apps: HTTPS → app.yourdomain.com → 60s interval

**Setup notifications:**
1. Settings → Notifications
2. Add method (Email/Slack/Discord)
3. Test channel
4. Assign to monitors

**Create status page:**
1. Status Pages → Add
2. Select monitors
3. Share public URL

## Incident Response

### Severity Matrix

| Priority | Definition | Response Time | Example |
|----------|-----------|---------------|---------|
| P0 | All services down | Immediate | Docker daemon crashed |
| P1 | Single service down | <15 min | App container stopped |
| P2 | Degraded performance | <1 hour | High CPU usage |
| P3 | Non-critical | <24 hours | Log rotation needed |

### Critical Incidents

#### System-Wide Outage (P0)
```bash
# 1. Check Docker
sudo systemctl restart docker

# 2. Verify Swarm
docker node ls
# If failed:
docker swarm leave --force && docker swarm init --advertise-addr $(curl -s ifconfig.me)

# 3. Redeploy
curl -sSL https://dokploy.com/install.sh | sh
cd ~ && docker compose -f docker-compose.kuma.yml up -d
```

#### Out of Memory (P1)
```bash
# Find OOM killed containers
dmesg | grep -i "out of memory"
docker ps -a | grep "Exited (137)"

# Restart
docker restart $(docker ps -aq)

# Permanent fix: Add limits in Dokploy
# App → Advanced → Memory Limit: 512M
```

#### Disk Full (P1)
```bash
# Emergency cleanup
docker system prune -a -f --volumes

# Find large files
du -sh /var/lib/docker/*
ncdu /  # Install: apt install ncdu

# Clean logs
truncate -s 0 /var/log/syslog
journalctl --vacuum-time=7d
```

#### Compromised Container (P0)
```bash
# Isolate
docker pause CONTAINER

# Capture evidence
docker logs CONTAINER > /root/incident-$(date +%Y%m%d).log
docker exec CONTAINER ps aux > /root/processes-$(date +%Y%m%d).txt

# Remove
docker stop CONTAINER && docker rm CONTAINER

# Redeploy from clean image
```

#### Certificate Expired (P1)
```bash
# Check expiry
echo | openssl s_client -connect deploy.yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates

# Force renewal
sudo rm /letsencrypt/acme.json && sudo touch /letsencrypt/acme.json
sudo chmod 600 /letsencrypt/acme.json
docker restart $(docker ps -qf name=traefik)
```

## Security Hardening

### Essential Checklist

- [ ] SSH: Key-only auth, no root, port 2222
- [ ] Firewall: UFW enabled (22/2222, 80, 443 only)
- [ ] Docker: Firewall bypass fix applied
- [ ] Fail2Ban: Monitoring SSH attempts
- [ ] Updates: Unattended-upgrades enabled
- [ ] Secrets: Not in Git, using .env files
- [ ] Containers: Running as non-root users
- [ ] Scanning: Trivy installed and used

### Verification

```bash
# SSH config
sudo grep -E "PermitRootLogin|PasswordAuthentication|Port" /etc/ssh/sshd_config

# Firewall
sudo ufw status numbered

# Fail2Ban
sudo fail2ban-client status sshd

# Container users
docker inspect $(docker ps -q) | grep '"User"'
```

### Advanced (Optional)

**CrowdSec** (Collaborative IPS)
```bash
curl -s https://packagecloud.io/install/repositories/crowdsec/crowdsec/script.deb.sh | sudo bash
sudo apt install crowdsec
```

**AppArmor** (Sandboxing)
```bash
sudo aa-status
sudo apt install apparmor-profiles
sudo aa-enforce /etc/apparmor.d/docker
```

## Backup Strategy

### What to Backup

1. Dokploy PostgreSQL database
2. Uptime Kuma data (~/kuma-data)
3. Application volumes
4. Config files (docker-compose.yml, etc.)

### Simple Backups (Included in weekly script)

Backs up to `/root/backups/`:
- Dokploy DB: `dokploy-YYYYMMDD.sql`
- Kuma data: `kuma-YYYYMMDD.tar.gz`

### Restic (Recommended for Production)

See `references/backup-s3.md` for full S3 configuration.

Local example:
```bash
sudo apt install restic

# Initialize
restic init --repo /mnt/backup

# Backup
docker exec dokploy-db pg_dump -U dokploy | restic backup --stdin --stdin-filename dokploy.sql --repo /mnt/backup

# Restore
restic restore latest --target /restore --repo /mnt/backup
```

### Restore Procedures

**Dokploy:**
```bash
docker stop dokploy
cat backup.sql | docker exec -i dokploy-db psql -U dokploy
docker start dokploy
```

**Kuma:**
```bash
docker compose -f ~/docker-compose.kuma.yml down
rm -rf ~/kuma-data && tar -xzf backup.tar.gz -C ~
docker compose -f ~/docker-compose.kuma.yml up -d
```

## Monitoring

### Key Metrics

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| CPU | <70% | 70-90% | >90% |
| Memory | <80% | 80-90% | >90% |
| Disk | <85% | 85-95% | >95% |
| Container restarts | 0 | 1-3 | >3 |

### View Metrics

```bash
# System
htop  # Install: apt install htop
free -h
df -h

# Docker
docker stats --no-stream
docker system df

# Logs
docker logs -f CONTAINER
journalctl -u docker -f
```

## Reference Files

- **scripts/daily-vps-check.sh** - Ready-to-use health check script
- **scripts/weekly-maintenance.sh** - Ready-to-use maintenance script
- **references/backup-s3.md** - S3 backup configuration with Restic
- **references/incident-template.md** - Incident documentation template

## Related Skills

- **vps-deployment-stack** - Infrastructure setup (prerequisite)
- **docker-development-workflow** - App development and CI/CD
