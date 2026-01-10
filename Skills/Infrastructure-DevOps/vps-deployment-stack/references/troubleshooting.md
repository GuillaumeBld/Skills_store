# Extended Troubleshooting Guide

## Less Common Issues

### Issue: Docker Swarm Node Unhealthy
**Symptoms:** `docker node ls` shows "Down" or "Unknown"

**Diagnosis:**
```bash
docker node ls
docker node inspect <node-id> | grep -A 10 Status
```

**Fix:**
```bash
# Rejoin swarm
docker swarm leave --force
docker swarm init --advertise-addr $(curl -s ifconfig.me)

# Redeploy Dokploy
curl -sSL https://dokploy.com/install.sh | sh
```

### Issue: Services Don't Start After Reboot
**Symptoms:** After VPS reboot, containers aren't running

**Diagnosis:**
```bash
sudo systemctl status docker
docker ps -a
```

**Fix:**
```bash
# Ensure Docker starts on boot
sudo systemctl enable docker
sudo systemctl start docker

# Restart services
docker compose -f ~/docker-compose.kuma.yml up -d

# Check Dokploy
docker service ls
```

### Issue: Traefik Not Routing New App
**Symptoms:** App deployed but domain returns 404

**Diagnosis:**
```bash
# Check Traefik sees the app
docker logs $(docker ps -qf name=traefik) 2>&1 | grep your-app-name

# Verify labels on container
docker inspect your-app-name | grep -A 10 Labels
```

**Fix:**
- Ensure app is on `dokploy-network`: `docker network inspect dokploy-network`
- Restart Traefik: `docker restart $(docker ps -qf name=traefik)`
- Verify DNS points to VPS: `dig app.yourdomain.com +short`

### Issue: Uptime Kuma Not Sending Notifications
**Symptoms:** Monitors trigger but no alerts received

**Diagnosis:**
- Check Kuma notification settings: Settings → Notifications
- Test notification: Click "Test" button
- Check logs: `docker logs uptime-kuma`

**Fix:**
- Verify SMTP credentials (email)
- Check webhook URLs are accessible
- Ensure VPS can reach external services (firewall)

### Issue: Port Conflicts
**Symptoms:** Service fails with "address already in use"

**Diagnosis:**
```bash
sudo ss -tlnp | grep :<port>
```

**Fix:**
- Stop conflicting service: `sudo systemctl stop <service>`
- Or change port in docker-compose.yml

### Issue: Build Timeout
**Symptoms:** Dokploy deployment fails with "build timed out"

**Fix:**
- Increase timeout: App Settings → Advanced → Build Timeout: 30m
- Or build externally and push to registry (see docker-development-workflow skill)

### Issue: Out of Memory During Build
**Symptoms:** Build fails, `dmesg | grep oom` shows OOM killer

**Fix:**
- Upgrade VPS RAM (temporary: add swap)
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Issue: Certificate Renewal Fails
**Symptoms:** Let's Encrypt cert expires, renewal fails

**Diagnosis:**
```bash
# Check Traefik logs
docker logs $(docker ps -qf name=traefik) 2>&1 | grep -i acme

# Verify acme.json
sudo ls -la /letsencrypt/acme.json
```

**Fix:**
```bash
# Manual renewal
docker restart $(docker ps -qf name=traefik)

# If persistent, delete and recreate
sudo rm /letsencrypt/acme.json
sudo touch /letsencrypt/acme.json
sudo chmod 600 /letsencrypt/acme.json
docker restart $(docker ps -qf name=traefik)
```

## Emergency Recovery Procedures

### Full System Recovery
If all services are down:

```bash
# 1. Check Docker daemon
sudo systemctl restart docker

# 2. Verify Swarm
docker node ls
# If failed, reinitialize:
docker swarm leave --force
docker swarm init --advertise-addr $(curl -s ifconfig.me)

# 3. Redeploy infrastructure
curl -sSL https://dokploy.com/install.sh | sh

# 4. Restore Uptime Kuma
cd ~ && docker compose -f docker-compose.kuma.yml up -d
```

### Disaster Recovery: Restore from Backup
See vps-daily-operations skill for backup/restore procedures.

## Performance Optimization

### Issue: Slow Deployments
**Diagnosis:** Check build cache

**Fix:**
- Enable Docker BuildKit: `DOCKER_BUILDKIT=1`
- Use multi-stage builds (see docker-development-workflow skill)
- Build on CI and push to registry

### Issue: High Memory Usage
**Diagnosis:**
```bash
docker stats
free -h
```

**Fix:**
- Set resource limits in Dokploy: App → Advanced → Resource Limits
- Stop unused containers
- Add swap (see above)

### Issue: High Disk I/O
**Diagnosis:**
```bash
iostat -x 5
docker system df
```

**Fix:**
- Use faster disk (NVMe SSD)
- Clean Docker cache: `docker system prune -a -f`
- Move Docker data to separate volume

## Debug Mode

Enable verbose logging:

**Traefik:**
```bash
# Add to Traefik config
log:
  level: DEBUG
```

**Dokploy:**
Check logs: `docker logs dokploy -f --tail 200`

**Docker:**
```bash
# Enable debug mode
sudo nano /etc/docker/daemon.json
{
  "debug": true,
  "log-level": "debug"
}
sudo systemctl restart docker
```
