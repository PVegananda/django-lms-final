# FINAL PROJECT REPORT — Pemrograman Sisi Server

## Identitas

| | |
|---|---|
| **Nama** | Pasyah Vegananda |
| **Kelas** | Pemrograman Sisi Server |
| **URL Repository** | https://github.com/PVegananda/DJANGO-LMS-FINAL-PROJECT |

---

## Deskripsi Project

Project ini adalah pengembangan lanjutan dari Simple LMS yang dikerjakan pada tugas-tugas
sebelumnya (modul 01–12). Project awal menggunakan Django biasa dengan views + templates,
kemudian dikembangkan menjadi REST API berbasis **Django Ninja** dengan fitur-fitur lanjutan.

Pengembangan mencakup:
- Refactor ke REST API dengan Django Ninja
- Integrasi Redis untuk caching dan session
- Integrasi MongoDB untuk analytics dan activity logging
- Integrasi RabbitMQ + Celery untuk asynchronous tasks
- Tambahan fitur tracking progress belajar, kategorisasi course, dan monitoring cache

---

## Fitur Dasar yang Sudah Berjalan

| Fitur | Status | Keterangan |
|-------|--------|------------|
| Docker Compose | ✅ | 7 services: app, db, redis, mongodb, rabbitmq, celery_worker, celery_beat |
| Database PostgreSQL | ✅ | Migration selesai, data ter-seed |
| Authentication JWT | ✅ | Login, register, refresh token |
| Role admin/instructor/student | ✅ | Diterapkan via `is_superuser` + owner check di setiap endpoint |
| Endpoint course | ✅ | CRUD + search + filter + pagination |
| Endpoint lesson/content | ✅ | CRUD per course |
| Endpoint enrollment | ✅ | Enroll, lihat my courses |
| Endpoint progress | ✅ | Update + lihat progress per konten |
| README lengkap | ✅ | Cara run, akun demo, endpoint list |
| Swagger/OpenAPI | ✅ | `/api/v1/docs`, `/api/v2/docs`, `/api/analytics/docs` |
| Struktur rapi, no hardcode secret | ✅ | Semua config via env variable |

---

## Fitur Tambahan yang Dikerjakan

### Paket 4 — Performance & API Quality (Redis Caching)

| Fitur | Poin | Status | Implementasi |
|-------|------|--------|-------------|
| Redis caching untuk course | 12 | ✅ | Cache course list + detail, TTL 5 menit |
| Cache invalidation strategy | 12 | ✅ | Cache dihapus saat create/update/delete |
| Cache monitoring | 10 | ✅ | `GET /api/v1/cache/status/` + `DELETE /api/v1/cache/clear/` |

**Total: 34 poin (dihitung 34)**

### Paket 5 — Analytics & Activity Tracking (MongoDB)

| Fitur | Poin | Status | Implementasi |
|-------|------|--------|-------------|
| Activity logging ke MongoDB | 15 | ✅ | Log saat view course, enroll |
| Aggregation query MongoDB | 15 | ✅ | Pipeline: daily active users, action summary |
| Course analytics report | 15 | ✅ | `GET /api/analytics/stats/popular-courses/` |

**Total: 45 poin (dihitung 45)**

### Paket 6 — Async Processing & Notification (Celery)

| Fitur | Poin | Status | Implementasi |
|-------|------|--------|-------------|
| Generate report async | 18 | ✅ | `POST /api/v1/reports/generate/{id}/` |
| Task status endpoint | 12 | ✅ | `GET /api/v1/reports/status/{task_id}/` |
| Scheduled task (Celery Beat) | 15 | ✅ | Daily stats + cleanup log setiap malam |
| Email notification async | 12 | ✅ | Task `send_enrollment_notification` |

**Total: 57 poin (dihitung 50, karena maks 50)**

**Estimasi total fitur tambahan: ~50 poin**

---

## Cara Menjalankan Project

```bash
# Clone repo
git clone <URL_REPO>
cd django-lms-final

# Setup environment
cp .env.example .env

# Jalankan Docker
docker compose up -d --build

# Migrasi database
docker compose exec app python manage.py migrate

# Isi data demo
docker compose exec app python manage.py seed_data
docker compose exec app python manage.py import_from_simplelms
docker compose exec app python manage.py seed_analytics --count 200

# Generate JWT key
docker compose exec app python manage.py make_jwt_key

# Buat admin
docker compose exec app python manage.py createsuperuser
```

---

## Akun Demo

| Role | Username | Password |
|------|----------|----------|
| Instructor | `dosen01` | `password123` |
| Instructor | `dosen02` | `password123` |
| Student | `siswa01` | `password123` |
| Student | `siswa02` | `password123` |
| Admin | (buat via createsuperuser) | (bebas) |

---

## Endpoint Penting

| Endpoint | Method | Keterangan |
|----------|--------|------------|
| `/api/v1/auth/sign-in` | POST | Login |
| `/api/v1/courses/` | GET | Daftar course (search, filter) |
| `/api/v1/course/{id}/enroll/` | POST | Daftar ke course |
| `/api/v1/progress/` | POST | Update progress belajar |
| `/api/v1/progress/my/` | GET | Progress saya |
| `/api/v1/reports/generate/{id}/` | POST | Generate report (async) |
| `/api/analytics/stats/action-summary/` | GET | Analytics MongoDB |
| `/api/v2/lab/course-list/optimized/` | GET | Demo DB optimization |

---

## Kendala dan Solusi

| Kendala | Solusi |
|---------|--------|
| JWT key tidak ada saat startup | Jalankan `make_jwt_key` setelah container up |
| Migration prompt interactive | Tulis migration file secara manual agar bisa dijalankan otomatis |
| MongoDB timeout saat analytics kosong | Tambah seed command `seed_analytics` |
| Celery task gagal silent | Tambah `try/except` di semua task call, error tidak merusak response |

---

## Kesimpulan

Project ini berhasil mengintegrasikan semua materi dari Modul 01–12:
- **Modul 01-04**: Django dasar, models, ORM
- **Modul 05**: DB optimization (select_related, prefetch_related, annotate)
- **Modul 06-08**: REST API dengan Django Ninja + JWT auth
- **Modul 09**: Automated testing
- **Modul 10**: Redis caching dan session
- **Modul 11**: MongoDB analytics
- **Modul 12**: Message brokers dengan Celery + RabbitMQ

Pengalaman terbesar: belajar bahwa setiap komponen (cache, async task, NoSQL) harus
diintegrasikan dengan hati-hati agar tidak saling merusak — error di MongoDB atau Celery
tidak boleh menggagalkan response API utama.
