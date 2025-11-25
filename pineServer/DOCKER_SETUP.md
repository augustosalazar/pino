# PineServer Docker Setup

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Using Docker directly

```bash
# Build the image
docker build -t pineserver .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e ROBLE_PROJECT_ID=tracking_7d2ad2db74 \
  -e ROBLE_BASE_URL=https://roble-api.openlab.uninorte.edu.co \
  -e ADMIN_EMAIL=admin@pine.com \
  -e ADMIN_PASSWORD=ThePassword!1 \
  --name pineserver \
  pineserver

# View logs
docker logs -f pineserver

# Stop the container
docker stop pineserver

# Remove the container
docker rm pineserver
```

## Environment Variables

The following environment variables are required:

- `ROBLE_PROJECT_ID`: Your Roble project ID
- `ROBLE_BASE_URL`: Roble API base URL
- `ADMIN_EMAIL`: Admin email for Roble authentication
- `ADMIN_PASSWORD`: Admin password for Roble authentication

## API Documentation

Once running, access the Swagger UI at:
- http://localhost:8000/docs

## Ports

- Container exposes port `8000`
- Maps to host port `8000`

## Network

The Docker Compose setup creates a bridge network called `pine-network` for potential future services.

## Updating the Container

```bash
# Rebuild and restart
docker-compose up -d --build

# Or with Docker directly
docker build -t pineserver .
docker stop pineserver
docker rm pineserver
docker run -d -p 8000:8000 -e ... pineserver
```

## Troubleshooting

### Check container status
```bash
docker ps -a
```

### View logs
```bash
docker-compose logs -f
# or
docker logs -f pineserver
```

### Access container shell
```bash
docker exec -it pineserver /bin/bash
```

### Restart container
```bash
docker-compose restart
# or
docker restart pineserver
```
