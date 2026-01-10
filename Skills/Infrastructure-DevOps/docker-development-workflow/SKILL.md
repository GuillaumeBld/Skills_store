---
name: docker-development-workflow
description: Docker development workflow patterns including local development setup with hot-reload, production Dockerfile optimization using multi-stage builds, docker-compose for dev/staging/prod environments, CI/CD pipeline configuration with GitHub Actions, image size reduction techniques (70-90% smaller), and release management strategies. Use when setting up local Docker development, optimizing container images, implementing CI/CD for containerized apps, or establishing deployment workflows from Git to production.
---

# Docker Development Workflow

Complete development workflow from local coding with hot-reload to production deployment via CI/CD.

## Prerequisites

- Docker Desktop (Mac/Windows) or Docker Engine (Linux) 20.10+
- Docker Compose v2
- Git repository for your application
- Basic understanding of Dockerfile syntax

## Quick Start: Local Development

### 1. Project Structure (2 min)

Organize your project:
```
my-app/
├── .github/workflows/
│   └── deploy.yml              # CI/CD pipeline
├── src/                        # Application code
├── Dockerfile                  # Production image
├── Dockerfile.dev              # Development image
├── docker-compose.yml          # Local development
├── docker-compose.prod.yml     # Production overrides
├── .dockerignore               # Exclude from build
├── .env.example                # Template (commit this)
└── .env                        # Secrets (DO NOT COMMIT)
```

### 2. Create Development Dockerfile (5 min)

**For Node.js:**
```dockerfile
# Dockerfile.dev
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

# Hot-reload with nodemon
CMD ["npm", "run", "dev"]
```

**For Python/Flask:**
```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Hot-reload with Flask
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]
```

### 3. Create docker-compose.yml (10 min)

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: myapp-dev
    ports:
      - "3000:3000"
    volumes:
      - ./src:/app/src:ro          # Mount source for hot-reload
      - /app/node_modules           # Prevent overwriting
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://user:pass@db:5432/myapp
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=myapp
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - app-network

volumes:
  db-data:

networks:
  app-network:
    driver: bridge
```

### 4. Development Workflow Commands

```bash
# Start environment
docker compose up -d

# View logs
docker compose logs -f app

# Run commands in container
docker compose exec app npm install new-package
docker compose exec app pytest

# Restart after config changes
docker compose restart app

# Stop all
docker compose down

# Rebuild after Dockerfile changes
docker compose build --no-cache app
docker compose up -d
```

## Production Dockerfile Optimization

### Multi-Stage Build Pattern

**Node.js Example:**
```dockerfile
# Dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine

WORKDIR /app

# Copy only production files
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

# Non-root user (CRITICAL for security)
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser
USER appuser

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

**Python Example:**
```dockerfile
# Dockerfile
# Stage 1: Dependencies
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

# Non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Size Reduction Techniques

**Before/After Results:**
- Using Alpine base: ~70% smaller (1.2GB → 180MB)
- Multi-stage builds: Additional 20-40% reduction
- Combined: 70-90% total reduction

**Best Practices:**
```dockerfile
# 1. Use Alpine base images
FROM python:3.11-alpine  # Not python:3.11

# 2. Combine RUN commands (reduces layers)
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. Order by change frequency
COPY package.json .      # Rarely changes → first
RUN npm install
COPY . .                 # Frequently changes → last

# 4. Use .dockerignore (see assets/dockerignore-template)
```

### .dockerignore Template

See `assets/dockerignore-template` for complete file.

Key exclusions:
```
.git
.env
node_modules
*.md
.vscode
__pycache__/
*.pyc
```

## Production docker-compose.yml

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: ghcr.io/your-username/myapp:latest
    restart: always
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}  # From .env
    volumes:
      - ./logs:/app/logs
    networks:
      - dokploy-network
    labels:
      # Traefik configuration
      - "traefik.enable=true"
      - "traefik.http.routers.myapp.rule=Host(`app.yourdomain.com`)"
      - "traefik.http.routers.myapp.entrypoints=websecure"
      - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
      - "traefik.http.services.myapp.loadbalancer.server.port=3000"

networks:
  dokploy-network:
    external: true
```

## CI/CD with GitHub Actions

### Basic Workflow (Build → Push → Deploy)

See `references/github-actions-template.yml` for complete workflow.

**Setup:**
1. Add GitHub Secrets:
   - `DOKPLOY_WEBHOOK_URL` (from Dokploy app settings)
   - `GITHUB_TOKEN` (automatic)

2. Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: docker/setup-buildx-action@v3
      
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Deploy to Dokploy
        run: |
          curl -X POST "${{ secrets.DOKPLOY_WEBHOOK_URL }}"
```

3. Configure Dokploy:
   - Set Docker Image: `ghcr.io/your-username/your-repo:latest`
   - Registry: GitHub Container Registry (GHCR)

### Multi-Environment Setup

For prod/staging/dev environments:
```yaml
jobs:
  deploy-production:
    if: github.ref == 'refs/heads/main'
    steps:
      - run: curl -X POST ${{ secrets.PROD_WEBHOOK }}

  deploy-staging:
    if: github.ref == 'refs/heads/staging'
    steps:
      - run: curl -X POST ${{ secrets.STAGING_WEBHOOK }}
```

Create separate Dokploy apps for each environment.

## Image Security

### Vulnerability Scanning

```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan image
trivy image myapp:latest

# Fail CI on HIGH/CRITICAL
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest
```

### Security Best Practices

```dockerfile
# 1. Always run as non-root
RUN adduser -D -u 1000 appuser
USER appuser

# 2. Pin base image versions (avoid drift)
FROM node:20.11.0-alpine3.19  # Not node:latest

# 3. Don't store secrets in image
# Use runtime environment variables instead

# 4. Scan regularly
# Add to CI/CD pipeline
```

## Common Development Scenarios

### Adding New Service (e.g., Redis)

Update `docker-compose.yml`:
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - app-network
  
  app:
    depends_on:
      - db
      - redis  # Add dependency
```

Restart:
```bash
docker compose up -d redis
docker compose restart app
```

### Debugging Containers

```bash
# View logs
docker compose logs app --tail 100 -f

# Enter container
docker compose exec app sh

# Check resources
docker stats

# Inspect network
docker network inspect myapp_app-network
```

### Database Migrations

```bash
# Run inside container
docker compose exec app npm run migrate
docker compose exec app python manage.py migrate
docker compose exec app bundle exec rake db:migrate
```

### Hot-Reload Not Working

**Fix for Node.js:**
```yaml
# docker-compose.yml
volumes:
  - ./src:/app/src:ro
  - /app/node_modules  # Anonymous volume (higher priority)

environment:
  - CHOKIDAR_USEPOLLING=true  # For Webpack/Vite
```

**Fix for Python:**
```yaml
volumes:
  - ./app:/app/app:ro  # Mount only app directory, not all
```

## Release Management

### Semantic Versioning

Use Git tags:
```bash
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3

# GitHub Actions builds: ghcr.io/user/repo:v1.2.3
```

### Rollback Procedure

**In Dokploy:**
1. App → Deployments
2. Find previous successful deployment
3. Click "Rollback"

**Via docker-compose:**
```bash
docker pull ghcr.io/user/repo:v1.2.2
docker tag ghcr.io/user/repo:v1.2.2 ghcr.io/user/repo:latest
docker compose -f docker-compose.prod.yml up -d app
```

## Reference Files

- **references/github-actions-template.yml** - Complete CI/CD workflows
- **references/dockerfile-patterns.md** - Language-specific Dockerfile patterns
- **assets/dockerignore-template** - Ready-to-use .dockerignore

## Related Skills

- **vps-deployment-stack** - Deploy to Dokploy infrastructure
- **vps-daily-operations** - Operational procedures and monitoring
