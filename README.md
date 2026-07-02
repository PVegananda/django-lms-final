# Django LMS Final Project

> **Mata Kuliah:** Pemrograman Sisi Server  
> **NIM:** A11.2025.16575  
> **Nama:** P. Vegananda

Project ini adalah pengembangan lanjutan dari **Simple LMS** yang dibuat di tugas sebelumnya.
Dibangun menggunakan **Django Ninja** (REST API) dengan stack lengkap:
PostgreSQL, Redis, MongoDB, RabbitMQ, dan Celery.

### Referensi Repository Sebelumnya

| Repo | Keterangan | Link |
|------|------------|------|
| **SimpleLMS** | Project awal (Tugas 1–5): Django + PostgreSQL, model dasar, DB optimization | https://github.com/PVegananda/simplelms |
| **Django Ninja** | Lanjutan (Tugas 6–13): REST API, JWT, Redis, MongoDB, Celery | https://github.com/PVegananda/django-ninja |
| **Final Project** | Repo ini — gabungan semua + fitur tambahan Final Project | (repo ini) |

### Dokumentasi Per Tugas

Setiap tugas sudah didokumentasikan dalam file `.md` masing-masing di folder `docs/`:

| File | Tugas | Materi |
|------|-------|--------|
| [`docs/tugas-01.md`](docs/tugas-01.md) | Setup Environment | Docker install, hello-world |
| [`docs/tugas-02.md`](docs/tugas-02.md) | Containerize App | Dockerfile, port mapping, volume |
| [`docs/tugas-03.md`](docs/tugas-03.md) | Multi-Container | Docker Compose, Django+PostgreSQL+Redis |
| [`docs/tugas-04.md`](docs/tugas-04.md) | Model dan Data | ERD, model, CSV import, query CRUD |
| [`docs/tugas-05.md`](docs/tugas-05.md) | Performance Testing | Django Silk, N+1, optimasi, benchmark |
| [`docs/tugas-06.md`](docs/tugas-06.md) | REST API | Django Ninja, schema, CRUD endpoints |
| [`docs/tugas-07.md`](docs/tugas-07.md) | Auth & Authorization | JWT, register, login, role check |
| [`docs/tugas-09.md`](docs/tugas-09.md) | Advanced API | Filter, sort, pagination, file upload, PATCH |
| [`docs/tugas-10.md`](docs/tugas-10.md) | Automated Testing | Unit test, integration test, coverage, locust |
| [`docs/tugas-11.md`](docs/tugas-11.md) | Redis | Cache, session, leaderboard, benchmark |
| [`docs/tugas-12.md`](docs/tugas-12.md) | MongoDB Analytics | Activity logging, aggregation pipeline |
| [`docs/tugas-13.md`](docs/tugas-13.md) | Message Brokers | Celery, RabbitMQ, periodic tasks, Flower |

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
# Seed data utama (users, courses, categories, reviews, dll)
docker compose exec app python manage.py seed_data

# Isi data analytics MongoDB
docker compose exec app python manage.py seed_analytics --count 200

# Generate JWT key (wajib untuk login)
docker compose exec app python manage.py make_jwt_key
```

### 5. Buat superuser (admin)
```bash
docker compose exec app python manage.py createsuperuser
```

### 6. Jalankan tests
```bash
# Jalankan semua test
docker compose exec app python manage.py test courses -v 2

# Dengan coverage report
docker compose exec app coverage run manage.py test courses
docker compose exec app coverage report
```

---

## Akun Demo

Setelah menjalankan `seed_data`, akun-akun berikut sudah tersedia:

| Role | Username | Password | Keterangan |
|------|----------|----------|------------|
| **Instructor** | `dosen01` – `dosen20` | `password123` | Teacher, role=instructor |
| **Student** | `mhs001` – `mhs080` | `password123` | Mahasiswa, role=student |
| **Admin** | (buat sendiri) | (buat sendiri) | Akses penuh via `createsuperuser` |

---

## Akses URL dan Login

> **Catatan:** Endpoint API (`/api/v1/`, `/api/v2/`, `/api/analytics/`) adalah **REST API** yang mengembalikan **JSON**, bukan halaman web HTML. Untuk mencoba endpoint, gunakan **Swagger UI** (link `/docs` di bawah) yang sudah menyediakan form interaktif.

| Layanan | URL | Keterangan / Login Default |
|---|---|---|
| **API v1 (Main)** | `http://localhost:8000/api/v1/docs` | Swagger Docs untuk semua core fitur LMS |
| **API v2 (Enhanced)** | `http://localhost:8000/api/v2/docs` | Swagger Docs teroptimasi (No N+1 queries) |
| **Analytics API** | `http://localhost:8000/api/analytics/docs` | MongoDB-based Analytics API Swagger Docs |
| **Django Admin** | `http://localhost:8000/admin/` | Panel admin backend<br>**Login:** `admin` / `password123` |
| **Django Silk** | `http://localhost:8000/silk/` | DB & Query Profiling (Tidak butuh login) |
| **RabbitMQ** | `http://localhost:15672/` | Celery Broker UI<br>**Login:** `guest` / `guest` |

### Cara Login API (Swagger UI)

1. Buka http://localhost:8000/api/v1/docs
2. Cari endpoint `POST /api/v1/auth/sign-in`
3. Klik "Try it out", isi body:
   ```json
   {
     "username": "dosen01",
     "password": "password123"
   }
   ```
4. Klik "Execute" → copy nilai `access` dari response
5. Klik tombol **"Authorize"** di pojok kanan atas Swagger
6. Paste token dengan format: `Bearer <token_yang_dicopy>`
7. Sekarang semua endpoint yang butuh auth bisa diakses

> [!WARNING]  
> **Akun `dosen01` atau `mhs001` BUKAN untuk Django Admin!**  
> Jika Anda mencoba login di `http://localhost:8000/admin/` menggunakan akun dosen/mahasiswa, pasti akan ditolak (error salah password/akun). Django Admin hanya bisa diakses oleh akun yang memiliki status *Staff/Superuser*. Silakan gunakan akun yang Anda buat melalui `docker compose exec app python manage.py createsuperuser`.

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

### Reviews (Final Project)
| Method | Endpoint | Auth | Keterangan |
|--------|----------|------|------------|
| POST | `/api/v1/reviews/` | ✅ | Buat review (hanya enrolled student, 1x per course) |
| GET | `/api/v1/reviews/course/{id}/` | — | Lihat review + rata-rata rating |
| PUT | `/api/v1/reviews/{id}/` | ✅ | Update review (pemilik only) |
| DELETE | `/api/v1/reviews/{id}/` | ✅ | Hapus review (pemilik/admin) |

### Dashboard (Final Project)
| Method | Endpoint | Auth | Keterangan |
|--------|----------|------|------------|
| GET | `/api/v1/dashboard/` | ✅ | Dashboard mahasiswa (enrolled courses, progress, rekomendasi) |

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
| `category_id` | `?category_id=1` | Filter berdasarkan kategori |
| `instructor` | `?instructor=dosen01` | Filter berdasarkan username dosen |
| `ordering` | `?ordering=price` | Urut: name, price, created_at (tambah `-` untuk descending) |
| `page` | `?page=2` | Pagination, 10 item per halaman |

---

## Fitur Final Project

| Fitur | Kategori | Implementasi |
|-------|----------|-------------|
| **Rating & Review** | Course Experience | Model Review, endpoint CRUD, rata-rata rating |
| **Student Dashboard** | Course Experience | Endpoint ringkasan: enrolled courses, progress, rekomendasi |
| **Search + Filter Lanjutan** | Course Experience | Filter category, instructor, search, sorting, pagination |
| **Role System** | Authentication | UserProfile dengan role admin/instructor/student |
| **Redis Caching** | Performance | Cache-aside pattern, invalidation, leaderboard |
| **MongoDB Analytics** | Analytics | Activity logging, aggregation pipeline, daily stats |
| **Celery Tasks** | Async Processing | Email notification, report generation, periodic cleanup |
| **Automated Testing** | Quality | 40+ test cases: unit, integration, RBAC |

---

## Stack Teknologi

| Komponen | Teknologi | Versi |
|----------|-----------|-------|
| Backend | Django + Django Ninja | 5.1 + 1.1 |
| Database | PostgreSQL | 16 |
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
│   │   ├── models.py     # Course, Category, Member, Content, Comment, Progress, Review, UserProfile
│   │   ├── apiv1.py      # REST API v1 (endpoint utama + review + dashboard)
│   │   ├── apiv2.py      # REST API v2 (enhanced + lab optimization)
│   │   ├── schemas.py    # Pydantic schemas (termasuk ReviewIn/ReviewOut)
│   │   ├── tasks.py      # Celery async tasks
│   │   ├── tests.py      # Test suite (40+ test cases)
│   │   └── filters.py    # Filter classes
│   ├── analytics/        # MongoDB analytics
│   ├── lms/              # Django project config
│   │   ├── settings.py   # Config (pakai env variables)
│   │   ├── celery.py     # Celery config
│   │   └── urls.py       # URL routing
│   ├── utils/            # Redis & MongoDB client helpers
│   └── fixtures/         # Data CSV dari SimpleLMS
├── docs/                 # Dokumentasi per tugas (01–13)
├── .env.example          # Template environment variables
├── docker-compose.yml    # Stack lengkap 7 services
├── Dockerfile
├── FINAL_PROJECT_REPORT.md
└── README.md
```
