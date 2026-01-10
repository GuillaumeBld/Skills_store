# Dockerfile Patterns by Language

Production-ready Dockerfile templates for common languages and frameworks.

## Node.js / TypeScript

### Express / NestJS / Next.js

```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy artifacts
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

# Non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

**Size:** ~180MB (vs 1.2GB with full node image)

## Python

### Flask / FastAPI / Django

```dockerfile
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

# Non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

**For Django:**
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
```

**Size:** ~200MB

## Go

```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source and build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Production stage - distroless for minimal size
FROM gcr.io/distroless/static-debian12

WORKDIR /app

# Copy binary
COPY --from=builder /app/main .

# Distroless runs as non-root by default
EXPOSE 8080

CMD ["./main"]
```

**Size:** ~15MB (Go binary + distroless base)

## Ruby / Rails

```dockerfile
# Build stage
FROM ruby:3.2-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache build-base postgresql-dev nodejs yarn

# Install gems
COPY Gemfile Gemfile.lock ./
RUN bundle config set --local deployment 'true' && \
    bundle config set --local without 'development test' && \
    bundle install

# Install JS dependencies
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# Copy app
COPY . .

# Precompile assets
RUN RAILS_ENV=production bundle exec rake assets:precompile

# Production stage
FROM ruby:3.2-alpine

WORKDIR /app

# Install runtime dependencies only
RUN apk add --no-cache postgresql-client nodejs

# Copy from builder
COPY --from=builder /usr/local/bundle /usr/local/bundle
COPY --from=builder /app /app

# Non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0"]
```

**Size:** ~400MB

## Java / Spring Boot

```dockerfile
# Build stage
FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /app

# Copy pom and download dependencies (cached layer)
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy source and build
COPY src ./src
RUN mvn package -DskipTests

# Production stage
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Copy JAR
COPY --from=builder /app/target/*.jar app.jar

# Non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown appuser:appuser app.jar
USER appuser

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**For Gradle:**
```dockerfile
FROM gradle:8-jdk21-alpine AS builder
COPY --chown=gradle:gradle . /app
WORKDIR /app
RUN gradle build --no-daemon
```

**Size:** ~300MB

## PHP / Laravel

```dockerfile
# Build stage
FROM composer:2 AS builder

WORKDIR /app

COPY composer.json composer.lock ./
RUN composer install --no-dev --optimize-autoloader --no-interaction

# Production stage
FROM php:8.2-fpm-alpine

WORKDIR /var/www/html

# Install extensions
RUN apk add --no-cache postgresql-dev && \
    docker-php-ext-install pdo pdo_pgsql

# Copy from builder
COPY --from=builder /app/vendor ./vendor
COPY . .

# Permissions
RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html/storage

USER www-data

EXPOSE 9000

CMD ["php-fpm"]
```

**With Nginx:**
```yaml
services:
  app:
    build: .
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

**Size:** ~150MB

## Rust

```dockerfile
# Build stage
FROM rust:1.75-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache musl-dev

# Copy Cargo files
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Copy real source and build
COPY . .
RUN touch src/main.rs && cargo build --release

# Production stage
FROM alpine:3.19

WORKDIR /app

# Copy binary
COPY --from=builder /app/target/release/myapp .

# Non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown appuser:appuser myapp
USER appuser

EXPOSE 8080

CMD ["./myapp"]
```

**Size:** ~10-20MB

## Static Site (HTML/JS)

### With Nginx

```dockerfile
FROM nginx:alpine

# Copy static files
COPY dist/ /usr/share/nginx/html/

# Custom nginx config (optional)
COPY nginx.conf /etc/nginx/nginx.conf

# Non-root user
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
```

**Size:** ~25MB

## Best Practices Summary

### 1. Use Smallest Base Image
- Alpine for most (5MB base)
- Distroless for Go/Rust (2MB base)
- Scratch for static binaries (0MB base)

### 2. Multi-Stage Builds
- Separate build and runtime stages
- Only copy artifacts needed for runtime
- Reduces image size by 70-90%

### 3. Layer Caching
```dockerfile
# Good: Dependencies change rarely
COPY package.json package-lock.json ./
RUN npm install

# Bad: Invalidates cache on any code change
COPY . .
RUN npm install
```

### 4. Non-Root User
**Always run as non-root:**
```dockerfile
RUN adduser -D -u 1000 appuser
USER appuser
```

### 5. Combine RUN Commands
```dockerfile
# Bad: 3 layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean

# Good: 1 layer
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### 6. Use .dockerignore
Exclude from build context:
```
.git
.env
node_modules
*.md
.vscode
__pycache__/
*.pyc
```

### 7. Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

### 8. Security Scanning
```bash
# Scan before pushing
trivy image myapp:latest

# Fail on HIGH/CRITICAL
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest
```

## Common Patterns

### Environment Variables
```dockerfile
# Set defaults
ENV NODE_ENV=production
ENV PORT=3000

# Override at runtime
docker run -e PORT=8080 myapp
```

### Secrets (DO NOT use ARG for secrets)
```dockerfile
# Bad - secrets in build history
ARG DATABASE_PASSWORD
RUN echo $DATABASE_PASSWORD > /app/.env

# Good - pass at runtime
docker run -e DATABASE_PASSWORD=secret myapp
```

### Build Arguments
```dockerfile
ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-alpine

# Build with custom version
docker build --build-arg NODE_VERSION=18 .
```

### Volumes
```dockerfile
# Declare volume mount points
VOLUME ["/app/data", "/app/logs"]

# Use in docker-compose
volumes:
  - ./data:/app/data
```

## Troubleshooting

### Image Too Large
1. Use Alpine base
2. Multi-stage build
3. Clean package cache
4. Remove dev dependencies

### Build Cache Not Working
1. Order layers by change frequency
2. Copy package files before source
3. Use `--cache-from` in CI

### Permission Denied
1. Run as non-root user
2. `chown` files to app user
3. Check file permissions (755/644)

### Container Crashes on Startup
1. Check logs: `docker logs container`
2. Test entrypoint: `docker run --entrypoint sh image`
3. Verify PORT binding (0.0.0.0, not 127.0.0.1)
