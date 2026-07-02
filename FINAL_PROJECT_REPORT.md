# Laporan Final Project — Django LMS

> **Mata Kuliah:** Pemrograman Sisi Server  
> **NIM:** A11.2025.16575  
> **Nama:** P. Vegananda

---

## 1. Deskripsi Project

Project ini adalah **Simple Learning Management System (LMS)** berbasis REST API yang
dibangun menggunakan Django Ninja. Project ini merupakan gabungan dari semua tugas
(Modul 01–13) yang kemudian dikembangkan lebih lanjut untuk memenuhi syarat Final Project.

### Repository Sebelumnya
- **SimpleLMS**: https://github.com/PVegananda/simplelms
- **Django Ninja**: https://github.com/PVegananda/django-ninja

---

## 2. Arsitektur Sistem

```
┌─────────────────┐
│   Client (API)  │
│  Swagger / curl │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Nginx  │ (opsional, production)
    └────┬────┘
         │
┌────────▼────────┐     ┌──────────┐
│  Django App     │────▶│PostgreSQL│  (Data utama)
│  (Django Ninja) │     └──────────┘
│                 │     ┌──────────┐
│  Port: 8000     │────▶│  Redis   │  (Cache, Session, Leaderboard)
│                 │     └──────────┘
│                 │     ┌──────────┐
│                 │────▶│ MongoDB  │  (Analytics, Activity Log)
└────────┬────────┘     └──────────┘
         │
    ┌────▼────┐     ┌──────────┐
    │ RabbitMQ│────▶│  Celery  │  (Background Tasks)
    └─────────┘     │  Worker  │
                    │  Beat    │
                    └──────────┘
```

### Stack Teknologi
| Komponen | Teknologi |
|----------|-----------|
| Backend | Django 5.1 + Django Ninja 1.1 |
| Database | PostgreSQL 16 |
| Cache | Redis 7 + django-redis |
| NoSQL | MongoDB 7 + pymongo |
| Message Broker | RabbitMQ 3 |
| Async Tasks | Celery 5.3 |
| Auth | JWT (ninja-simple-jwt) |
| Containerization | Docker + Docker Compose |

---

## 3. Komponen Wajib (30 Poin)

| Item | Status | Implementasi |
|------|--------|-------------|
| Docker Compose berjalan | ✅ | 7 services: app, database, redis, mongodb, rabbitmq, celery_worker, celery_beat |
| PostgreSQL + migration | ✅ | 5 migration files (0001–0005) |
| Authentication JWT | ✅ | ninja-simple-jwt: sign-in, token-refresh |
| Role system | ✅ | UserProfile.role: admin, instructor, student + signal auto-create |
| Endpoint CRUD lengkap | ✅ | Course, Content, Comment, Enrollment, Progress, Review, Category |
| README lengkap | ✅ | Cara menjalankan, akun demo, endpoint, stack |
| Swagger/OpenAPI | ✅ | 3 Swagger UI: /api/v1/docs, /api/v2/docs, /api/analytics/docs |
| Struktur rapi, no hardcode | ✅ | .env.example, docker-compose pakai ${VARIABLE:-default} |

---

## 4. Fitur Tambahan (Maks 50 Poin)

### A. Course Experience

#### Rating & Review Course (12 poin)
- Model `Review` dengan rating 1-5, komentar, unique per user-course
- Endpoint CRUD: `POST /reviews/`, `GET /reviews/course/{id}/`, `PUT /reviews/{id}/`, `DELETE /reviews/{id}/`
- Validasi: hanya enrolled student yang bisa review
- Rata-rata rating dihitung via aggregation (Avg)
- Cache invalidation saat review berubah

#### Student Dashboard (12 poin)
- Endpoint `GET /dashboard/` menampilkan:
  - Info profil (username, role, email)
  - Course yang diikuti (nama, role)
  - Progress keseluruhan (total tracked, completed, completion rate)
  - Review yang pernah diberikan
  - Rekomendasi course populer yang belum diikuti

#### Search + Filter Lanjutan (12 poin)
- Parameter `?search=` untuk pencarian nama/deskripsi (case-insensitive)
- Parameter `?category_id=` untuk filter berdasarkan kategori
- Parameter `?instructor=` untuk filter berdasarkan username pengajar
- Parameter `?ordering=` dengan whitelist (name, price, created_at)
- Pagination 10 item per halaman

### D. Redis & Performance

#### Caching (12 poin)
- Cache-aside pattern di GET /courses/{id}
- Cache invalidation saat create/update/delete course dan review
- Cache key management: `cache/status/` dan `cache/clear/`
- Session backend pakai Redis

#### Query Optimization (15 poin)
- `select_related()` dan `prefetch_related()` di semua endpoint
- Lab comparison: baseline vs optimized (API v2)
- N+1 query problem solved

### E. MongoDB & Analytics

#### Activity Logging (15 poin)
- Activity log di MongoDB saat user view course dan enroll
- Silent error handling (MongoDB down tidak merusak response)
- Seed command untuk generate data analytics

#### Aggregation Pipeline (15 poin)
- Action summary: `$group` by action type
- Active users: `$group` by username + `$sort`
- Popular courses: `$match` + `$group` + `$addToSet` unique users
- Daily stats: 7 hari terakhir

### F. Celery & Async

#### Email Notification (12 poin)
- `send_enrollment_notification.delay(user_id, course_id)`
- Retry mechanism: 3x dengan delay 60 detik
- Silent di caller (Celery down tidak merusak API)

#### Scheduled Tasks (15 poin)
- `generate_daily_stats`: setiap hari pukul 00:00
- `cleanup_old_logs`: setiap hari pukul 02:00

#### Task Status (12 poin)
- `POST /reports/generate/{course_id}/` → dapat task_id
- `GET /reports/status/{task_id}/` → cek PENDING/STARTED/SUCCESS/FAILURE

---

## 5. Testing

### Test Suite
File: `code/courses/tests.py`

| Kategori | Jumlah Test | Detail |
|----------|-------------|--------|
| Unit Test Model | 13 | Course, CourseMember, Review, UserProfile, Category |
| Integration Test Auth | 4 | Register, login, duplikat, password salah |
| Integration Test CRUD | 12 | List, detail, create, update, delete, search, filter |
| Integration Test Enrollment | 7 | Enroll, duplikat, progress |
| Integration Test Review | 7 | Create, duplikat, invalid rating, list, delete |
| Integration Test Dashboard | 2 | Data ringkasan, akses tanpa token |
| Test Permission/RBAC | 11 | 401 tanpa token, 403 tanpa izin, admin access |
| **Total** | **56** | |

### Cara Jalankan
```bash
docker compose exec app python manage.py test courses -v 2
docker compose exec app coverage run manage.py test courses
docker compose exec app coverage report
```

---

## 6. Model Database

```
┌───────────────┐     ┌────────────────┐     ┌──────────────┐
│  UserProfile  │     │    Category     │     │    Review     │
│ ─────────────│     │ ──────────────  │     │ ────────────  │
│ user (1:1)   │     │ name (unique)  │     │ user (FK)    │
│ role         │     │ description    │     │ course (FK)  │
│ bio          │     │ created_at     │     │ rating (1-5) │
└───────┬───────┘     └───────┬────────┘     │ comment      │
        │                     │              └──────────────┘
        ▼                     ▼
┌───────────────┐     ┌────────────────┐
│     User      │     │    Course       │
│ ─────────────│     │ ──────────────  │
│ (Django auth)│◄────│ teacher (FK)   │
└───────┬───────┘     │ category (FK)  │
        │             │ name, price    │
        │             └───────┬────────┘
        │                     │
        ▼                     ▼
┌───────────────┐     ┌────────────────┐     ┌──────────────┐
│ CourseMember  │     │ CourseContent   │     │   Progress   │
│ ─────────────│     │ ──────────────  │     │ ────────────  │
│ user (FK)    │     │ course (FK)    │     │ user (FK)    │
│ course (FK)  │     │ name           │     │ course (FK)  │
│ roles        │     │ file_attachment│     │ content (FK) │
└───────────────┘     └───────┬────────┘     │ status       │
                              │              └──────────────┘
                              ▼
                      ┌────────────────┐
                      │   Comment       │
                      │ ──────────────  │
                      │ content (FK)   │
                      │ user (FK)      │
                      │ comment        │
                      └────────────────┘
```

---

## 7. Git History

Project ini memiliki git history yang bersih dan bermakna.
Setiap commit menjelaskan perubahan yang dilakukan:

```
- init: Django LMS Final Project
- hapus file sensitif dan update gitignore
- tambah model Category dan Progress
- settings pakai env variable
- tambah endpoint Progress, Category, dan Cache Status
- update README lengkap
- tambah FINAL_PROJECT_REPORT.md
- tambah dokumentasi per tugas dan referensi repo sebelumnya
- tambah model UserProfile untuk role system
- pindahkan credential docker-compose ke environment variable
- tambah model Review untuk rating course
- tambah endpoint review course (buat, lihat, update, hapus)
- tambah endpoint dashboard mahasiswa
- tambah filter category dan instructor di pencarian course
- tambah seed data kategori, review, dan role UserProfile
- tambah test suite lengkap untuk model dan endpoint
- update README dan laporan Final Project
```

---

## 8. Cara Menjalankan

```bash
# 1. Clone repo
git clone <URL_REPO> && cd django-lms-final

# 2. Setup environment
cp .env.example .env

# 3. Jalankan Docker
docker compose up -d --build

# 4. Setup database
docker compose exec app python manage.py migrate
docker compose exec app python manage.py seed_data
docker compose exec app python manage.py seed_analytics --count 200
docker compose exec app python manage.py make_jwt_key
docker compose exec app python manage.py createsuperuser

# 5. Akses
# Swagger:  http://localhost:8000/api/v1/docs
# Admin:    http://localhost:8000/admin/
# RabbitMQ: http://localhost:15672/
```

---

## 9. Kesimpulan

Project ini berhasil menggabungkan semua materi dari Modul 01–13 menjadi satu
sistem LMS yang terintegrasi. Fitur tambahan Final Project (Rating & Review,
Student Dashboard, Search Filter Lanjutan, Testing) memberikan nilai tambah
yang signifikan terhadap kualitas project.

Arsitektur multi-container (Django + PostgreSQL + Redis + MongoDB + RabbitMQ + Celery)
menunjukkan pemahaman tentang bagaimana komponen backend bekerja sama dalam
sistem yang production-ready.
