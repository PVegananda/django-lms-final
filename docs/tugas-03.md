# Tugas 3: Multi-Container Application

## Ketentuan Tugas
1. Buat aplikasi dengan stack: Django + PostgreSQL + Redis
2. Buat docker-compose.yml dengan service, network, volumes, health check
3. Verifikasi semuanya terkoneksi

## Implementasi di Project Ini

### 1. Stack yang Digunakan
Project ini menggunakan 7 services, lebih dari yang diminta:

| Service | Image | Fungsi |
|---------|-------|--------|
| `app` | python:3.11-slim (custom) | Django REST API |
| `database` | postgres:16 | Database utama |
| `redis` | redis:7-alpine | Cache, session, Celery result |
| `mongodb` | mongo:7 | Analytics & activity log |
| `rabbitmq` | rabbitmq:3-management | Message broker |
| `celery_worker` | (sama dengan app) | Background task worker |
| `celery_beat` | (sama dengan app) | Periodic task scheduler |

### 2. Docker Compose Configuration
File: [`docker-compose.yml`](../docker-compose.yml)

**Named Volumes** untuk data persistence:
```yaml
volumes:
  postgres_data:     # data PostgreSQL
  redis_data:        # data Redis
  mongodb_data:      # data MongoDB
  rabbitmq_data:     # data RabbitMQ
```

**Health Check** untuk database:
```yaml
database:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s
    timeout: 5s
    retries: 5

rabbitmq:
  healthcheck:
    test: rabbitmq-diagnostics -q ping
    interval: 10s
    timeout: 5s
    retries: 5
```

**depends_on** memastikan urutan start:
```yaml
app:
  depends_on:
    database:
      condition: service_healthy
    redis:
      condition: service_started
    mongodb:
      condition: service_started
    rabbitmq:
      condition: service_healthy
```

### 3. Verifikasi Koneksi

**PostgreSQL:**
```bash
docker compose exec app python manage.py dbshell
# \dt  → menampilkan tabel-tabel Django
```

**Redis:**
```bash
docker compose exec redis redis-cli ping
# output: PONG
```

**MongoDB:**
```bash
docker compose exec mongodb mongosh -u admin -p password123
# show dbs → menampilkan database lms_analytics
```

### 4. Network
Semua service berada di network Docker Compose default.
Komunikasi antar container menggunakan nama service sebagai hostname:
- `database` untuk PostgreSQL
- `redis` untuk Redis
- `mongodb` untuk MongoDB
- `rabbitmq` untuk RabbitMQ

### File Terkait
- [`docker-compose.yml`](../docker-compose.yml) — semua services
- [`code/lms/settings.py`](../code/lms/settings.py) — konfigurasi koneksi
