# Tugas 2: Containerize Python Application

## Ketentuan Tugas
1. Buat aplikasi Python dengan endpoint GET / dan GET /api/info
2. Buat Dockerfile
3. Build image dan jalankan container dengan port mapping dan volume mount
4. Bonus: multi-stage build

## Implementasi di Project Ini

### 1. Dockerfile
File: [`Dockerfile`](../Dockerfile)

```dockerfile
FROM python:3.11-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY code/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY code /code/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 2. Port Mapping
Di `docker-compose.yml`, app service menggunakan port mapping:
```yaml
ports:
  - "8000:8000"  # host:container
```

### 3. Volume Mount (Development Mode)
```yaml
volumes:
  - ./code:/code  # kode di-mount langsung, perubahan langsung terefleksi
```

Dengan volume mount ini, kita bisa edit kode di host dan langsung terlihat di container
tanpa perlu rebuild image. Ini mode development.

### 4. Endpoint yang Tersedia
Project ini lebih dari sekadar hello world:

| Endpoint | Keterangan |
|----------|------------|
| `GET /api/v1/hello/` | Test endpoint — "Menyala abangkuh ..." |
| `GET /api/v1/docs` | Swagger UI dengan semua endpoint |
| `GET /api/v1/courses/` | Daftar course (data nyata) |

### 5. Build dan Run
```bash
# Build image
docker compose build

# Jalankan semua services
docker compose up -d

# Cek app berjalan
curl http://localhost:8000/api/v1/hello/
```

### File Terkait
- [`Dockerfile`](../Dockerfile)
- [`docker-compose.yml`](../docker-compose.yml)
- [`code/requirements.txt`](../code/requirements.txt)
