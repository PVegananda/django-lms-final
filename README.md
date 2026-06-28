# Django LMS Final Project

Project ini adalah pengembangan lanjutan dari **Simple LMS** yang dibuat di tugas sebelumnya.
Dibangun menggunakan **Django Ninja** (REST API) dengan stack lengkap:
PostgreSQL, Redis, MongoDB, RabbitMQ, dan Celery.

---

## Cara Menjalankan

### Prasyarat
- Docker Desktop sudah terinstall dan berjalan
- Git

### 1. Clone dan setup environment
```bash
git clone <URL_REPO_INI>
cd django-lms-final

# Salin template env
cp .env.example .env
# (opsional) edit .env jika ingin ubah password atau konfigurasi lain
```

### 2. Jalankan semua services
```bash
docker compose up -d --build
```

Services yang akan berjalan:
| Service | Port | Keterangan |
|---------|------|------------|
| `app` | 8000 | Django API |
| `database` | 5436 | PostgreSQL |
| `redis` | 6379 | Cache + Session + Celery result |
| `mongodb` | 27017 | Analytics & activity log |
| `rabbitmq` | 5672 / 15672 | Message broker (UI: :15672) |
| `celery_worker` | — | Async task worker |
| `celery_beat` | — | Periodic task scheduler |

### 3. Jalankan migrasi database
```bash
docker compose exec app python manage.py migrate
```

### 4. Isi data demo
```bash
# Seed data utama (users, courses, contents, dll)
docker compose exec app python manage.py seed_data

# Import data dari SimpleLMS (project sebelumnya)
docker compose exec app python manage.py import_from_simplelms

# Isi data analytics MongoDB
docker compose exec app python manage.py seed_analytics --count 200

# Generate JWT key (wajib untuk login)
docker compose exec app python manage.py make_jwt_key
```

### 5. Buat superuser (admin)
```bash
docker compose exec app python manage.py createsuperuser
```

---

## Akun Demo

Setelah menjalankan `seed_data`, akun-akun berikut sudah tersedia:

| Role | Username | Password | Keterangan |
|------|----------|----------|------------|
| **Instructor** | `dosen01` | `password123` | Teacher course 1-10 |
| **Instructor** | `dosen02` | `password123` | Teacher course 11-20 |
| **Student** | `siswa01` | `password123` | Enrolled di beberapa course |
| **Student** | `siswa02` | `password123` | Enrolled di beberapa course |
| **Admin** | (buat sendiri) | (buat sendiri) | Akses penuh via `createsuperuser` |

---

## Dokumentasi API (Swagger)

| API | URL | Keterangan |
|-----|-----|------------|
| **API v1** | http://localhost:8000/api/v1/docs | Endpoint utama LMS |
| **API v2** | http://localhost:8000/api/v2/docs | Enhanced + Lab Optimization |
| **Analytics** | http://localhost:8000/api/analytics/docs | MongoDB analytics |
| **Admin Panel** | http://localhost:8000/admin/ | Django Admin |
| **DB Profiling** | http://localhost:8000/silk/ | Query profiler |
| **RabbitMQ UI** | http://localhost:15672/ | `admin` / `password123` |

---

## Endpoint Penting

### Authentication
| Method | Endpoint | Keterangan |
|--------|----------|------------|
| POST | `/api/v1/register/` | Daftar akun baru |
| POST | `/api/v1/auth/sign-in` | Login, dapat JWT token |
| POST | `/api/v1/auth/token-refresh` | Refresh access token |

### Courses
| Method | Endpoint | Auth | Keterangan |
|--------|----------|------|------------|
| GET | `/api/v1/courses/` | — | Daftar course (search, filter, sort, pagination) |
| GET | `/api/v1/courses/{id}` | — | Detail course |
| POST | `/api/v1/courses/` | ✅ | Buat course baru |
| PUT | `/api/v1/courses/{id}` | ✅ | Update course (owner only) |
| DELETE | `/api/v1/courses/{id}` | ✅ | Hapus course (owner/admin) |
| GET | `/api/v1/courses/popular/` | — | Top 10 course (Redis leaderboard) |
| POST | `/api/v1/course/{id}/enroll/` | ✅ | Daftar ke course |
| GET | `/api/v1/mycourses/` | ✅ | Course yang diikuti |

### Progress Belajar
| Method | Endpoint | Auth | Keterangan |
|--------|----------|------|------------|
| POST | `/api/v1/progress/` | ✅ | Update status belajar per konten |
| GET | `/api/v1/progress/my/` | ✅ | Progress saya + completion rate |
| GET | `/api/v1/progress/course/{id}/` | ✅ (teacher) | Summary progress semua student |

### Category & Filter
| Method | Endpoint | Auth | Keterangan |
|--------|----------|------|------------|
| GET | `/api/v1/categories/` | — | Daftar kategori |
| POST | `/api/v1/categories/` | ✅ (admin) | Buat kategori |

### Contents & Comments
| Method | Endpoint | Auth | Keterangan |
|--------|----------|------|------------|
| GET | `/api/v1/contents/` | — | Daftar konten (filter by course) |
| POST | `/api/v1/contents/` | ✅ | Buat konten (teacher only) |
| POST | `/api/v1/comments/` | ✅ | Komentar konten (harus enrolled) |

### Reports (Celery Async)
| Method | Endpoint | Auth | Keterangan |
|--------|----------|------|------------|
| POST | `/api/v1/reports/generate/{course_id}/` | ✅ | Generate report (async) |
| GET | `/api/v1/reports/status/{task_id}/` | — | Cek status task |

### Analytics (MongoDB)
| Method | Endpoint | Keterangan |
|--------|----------|------------|
| GET | `/api/analytics/stats/action-summary/` | Ringkasan aksi user |
| GET | `/api/analytics/stats/active-users/` | Top active users |
| GET | `/api/analytics/stats/popular-courses/` | Course paling banyak dikunjungi |
| GET | `/api/analytics/stats/daily/` | Statistik harian |

### Cache & Monitoring
| Method | Endpoint | Auth | Keterangan |
|--------|----------|------|------------|
| GET | `/api/v1/cache/status/` | ✅ (admin) | Lihat Redis cache keys |
| DELETE | `/api/v1/cache/clear/` | ✅ (admin) | Bersihkan cache |

---

## Query Parameters (GET /courses/)

| Parameter | Contoh | Keterangan |
|-----------|--------|------------|
| `search` | `?search=Python` | Cari berdasarkan nama/deskripsi |
| `ordering` | `?ordering=price` | Urut: name, price, created_at (tambah `-` untuk descending) |
| `page` | `?page=2` | Pagination, 10 item per halaman |

---

## Stack Teknologi

| Komponen | Teknologi | Versi |
|----------|-----------|-------|
| Backend | Django + Django Ninja | 5.1 + 1.1 |
| Database | PostgreSQL | 15 |
| Cache | Redis + django-redis | 7 |
| NoSQL | MongoDB + pymongo | 7 + 4.6 |
| Message Broker | RabbitMQ | 3 |
| Async Tasks | Celery + Celery Beat | 5.3 |
| Auth | JWT (ninja-simple-jwt) | — |
| Profiling | Django Silk | 5.1 |
| Container | Docker + Docker Compose | — |

---

## Struktur Project

```
django-lms-final/
├── code/
│   ├── courses/          # App utama LMS
│   │   ├── models.py     # Course, Category, Member, Content, Comment, Progress
│   │   ├── apiv1.py      # REST API v1 (endpoint utama)
│   │   ├── apiv2.py      # REST API v2 (enhanced + lab optimization)
│   │   ├── schemas.py    # Pydantic schemas
│   │   ├── tasks.py      # Celery async tasks
│   │   └── filters.py    # Filter classes
│   ├── analytics/        # MongoDB analytics
│   ├── lms/              # Django project config
│   │   ├── settings.py   # Config (pakai env variables)
│   │   ├── celery.py     # Celery config
│   │   └── urls.py       # URL routing
│   ├── utils/            # Redis & MongoDB client helpers
│   └── fixtures/         # Data CSV dari SimpleLMS
├── .env.example          # Template environment variables
├── docker-compose.yml    # Stack lengkap 7 services
└── Dockerfile
```
