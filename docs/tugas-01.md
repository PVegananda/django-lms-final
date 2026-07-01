# Tugas 1: Setup Environment

## Ketentuan Tugas
1. Install Docker Desktop di komputer
2. Verifikasi instalasi dengan `docker run hello-world`
3. Clone repository project
4. Screenshot hasil verifikasi

## Implementasi di Project Ini

### 1. Docker Desktop
Docker Desktop sudah terinstall dan digunakan untuk menjalankan seluruh stack project ini.
Semua services berjalan di atas Docker menggunakan `docker-compose.yml`.

### 2. Verifikasi Docker
```bash
# verifikasi docker berjalan
docker --version
# output: Docker version 27.x.x

docker run hello-world
# output: Hello from Docker! ...
```

### 3. Clone Repository
```bash
git clone https://github.com/PVegananda/DJANGO-LMS-FINAL-PROJECT.git
cd django-lms-final
```

### 4. Bukti Docker Berjalan
Seluruh project berjalan di atas Docker Compose dengan 7 services:
```bash
docker compose up -d --build
docker compose ps
```

Output `docker compose ps` menampilkan:
| Container | Image | Status |
|-----------|-------|--------|
| lms-app | django-lms-final | Up |
| lms-db | postgres:16 | Up (healthy) |
| lms-redis | redis:7-alpine | Up |
| lms-mongodb | mongo:7 | Up |
| lms-rabbitmq | rabbitmq:3-management | Up (healthy) |
| lms-celery-worker | django-lms-final | Up |
| lms-celery-beat | django-lms-final | Up |

### File Terkait
- [`docker-compose.yml`](../docker-compose.yml) — definisi semua services
- [`Dockerfile`](../Dockerfile) — build image Python/Django
