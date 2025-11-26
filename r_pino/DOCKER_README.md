# Pino Web - Docker Deployment

This directory contains Docker configuration for building and deploying the Pino web application.

## 📋 Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)

## 🚀 Quick Start

### Build and Run with Docker Compose

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The application will be available at: **http://localhost:3000**

### Build Manually

```bash
# Build the image
docker build -t pino-web .

# Run the container
docker run -d -p 3000:80 --name pino-web pino-web

# View logs
docker logs -f pino-web

# Stop and remove
docker stop pino-web
docker rm pino-web
```

## 🏗️ Build Process

The Dockerfile uses a **multi-stage build** for optimization:

### Stage 1: Builder
- Base: `node:18-alpine`
- Installs dependencies
- Builds the Expo web app using `expo export:web`
- Output: Optimized static files in `/dist`

### Stage 2: Production
- Base: `nginx:alpine` (minimal footprint ~20MB)
- Copies built files from builder stage
- Serves static files with optimized nginx config
- Final image size: ~40MB

## ⚙️ Configuration

### Environment Variables

Currently no environment variables are required for the web build. If you need to add API URLs or other configs:

1. Create `.env.production` in the project root
2. Add your variables (they'll be baked into the build)
3. Access via `process.env` in your code

### Nginx Configuration

The `nginx.conf` file includes:
- **Gzip compression** for faster load times
- **Caching headers** for static assets (1 year)
- **SPA routing** - serves `index.html` for all routes
- **Security headers** (X-Frame-Options, etc.)

### Port Configuration

Default port is `3000`. To change:

**Docker Compose:**
```yaml
ports:
  - "8080:80"  # Change 8080 to your desired port
```

**Docker Run:**
```bash
docker run -d -p 8080:80 pino-web
```

## 🔍 Troubleshooting

### Build fails with "MODULE_NOT_FOUND"
```bash
# Clear node_modules and rebuild
rm -rf node_modules package-lock.json
npm install
docker-compose build --no-cache
```

### Container exits immediately
```bash
# Check logs
docker-compose logs web

# Common issue: Missing dist folder
# Ensure the build completes successfully in Stage 1
```

### App not loading
```bash
# Check if container is running
docker ps

# Check nginx logs
docker exec pino-web cat /var/log/nginx/error.log

# Verify files were copied correctly
docker exec pino-web ls -la /usr/share/nginx/html
```

## 📊 Performance Optimizations

The Docker setup includes several optimizations:

1. **Multi-stage build** - Reduces final image size by ~80%
2. **Gzip compression** - Reduces transfer size by ~70%
3. **Asset caching** - Browser caches static files for 1 year
4. **Alpine base** - Minimal OS footprint
5. **Health checks** - Auto-restart on failure

## 🚢 Production Deployment

### Using Docker Compose

1. **Update ports** in `docker-compose.yml` if needed
2. **Build and deploy:**
   ```bash
   docker-compose up -d --build
   ```

### Push to Registry

```bash
# Tag the image
docker tag pino-web:latest your-registry.com/pino-web:latest

# Push to registry
docker push your-registry.com/pino-web:latest

# Pull and run on production
docker pull your-registry.com/pino-web:latest
docker run -d -p 80:80 your-registry.com/pino-web:latest
```

### Using Docker Hub

```bash
# Login
docker login

# Tag
docker tag pino-web your-username/pino-web:latest

# Push
docker push your-username/pino-web:latest
```

## 🔐 Security Considerations

- Nginx runs as non-root user
- Security headers included in nginx config
- No sensitive data in the image (environment variables)
- Health checks enabled for monitoring

## 📝 Notes

- The web build is **static** - all API calls go to your backend
- Make sure your backend CORS settings allow your domain
- For HTTPS, use a reverse proxy (nginx, traefik, etc.) in front

## 🛠️ Development vs Production

This Dockerfile is for **production** deployment. For development:

```bash
# Run Expo dev server (not Docker)
npm start
# Press 'w' for web
```

## 📈 Monitoring

### Health Check

The container includes a health check that runs every 30 seconds:
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' pino-web
```

### Resource Usage

```bash
# Monitor CPU/Memory
docker stats pino-web

# View logs
docker logs -f --tail 100 pino-web
```

## 🤝 Contributing

To modify the Docker setup:
1. Edit `Dockerfile` or `nginx.conf`
2. Test locally: `docker-compose up --build`
3. Verify functionality
4. Update this README if needed
