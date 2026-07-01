# Tugas 5: Performance Testing dan Optimization

## Ketentuan Tugas
1. Setup Profiling (Django Silk) — 10 poin
2. Data Seed dengan bulk_create — 10 poin
3. Identifikasi N+1 Problem — 20 poin
4. Optimasi (select_related, prefetch_related, index, annotate) — 30 poin
5. Benchmark Report — 30 poin

## Implementasi di Project Ini

### 1. Setup Profiling — Django Silk (10 poin)

Django Silk sudah terpasang dan berjalan di project ini.

Konfigurasi di [`code/lms/settings.py`](../code/lms/settings.py):
```python
INSTALLED_APPS = [
    ...
    "silk",  # Django Silk - query profiling
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "silk.middleware.SilkyMiddleware",  # posisi awal
    ...
]

SILKY_PYTHON_PROFILER = True
SILKY_META = True
```

Dashboard profiling: http://localhost:8000/silk/

### 2. Data Seed dengan bulk_create (10 poin)

File: [`code/courses/management/commands/seed_data.py`](../code/courses/management/commands/seed_data.py)

Data yang di-seed:
- 100 courses
- 20 teachers (User)
- 500+ course members
- 300+ course contents
- 1000+ comments

```bash
docker compose exec app python manage.py seed_data
```

### 3. Identifikasi N+1 Problem (20 poin)

Endpoint lab optimization tersedia di API v2 untuk demonstrasi:

| Endpoint | Tipe | Masalah |
|----------|------|---------|
| `GET /api/v2/lab/course-list/baseline/` | N+1 | Setiap course melakukan query ke User |
| `GET /api/v2/lab/course-members/baseline/` | N+1 | Setiap member melakukan query terpisah |
| `GET /api/v2/lab/course-dashboard/baseline/` | 3N+1 | Count member + content per course |

### 4. Optimasi (30 poin)

Semua endpoint yang dioptimasi:

| Teknik | Di mana | Efek |
|--------|---------|------|
| `select_related('teacher')` | `GET /api/v1/courses/` | 1 query (JOIN) bukan N+1 |
| `prefetch_related('coursecontent_set')` | `GET /api/v1/courses/{id}` | 2 query bukan N+1 |
| `annotate(Count())` | `GET /api/v2/lab/course-dashboard/optimized/` | 1 query bukan 3N+1 |

Contoh kode optimasi di [`code/courses/apiv2.py`](../code/courses/apiv2.py):
```python
# Baseline: N+1 problem
courses = Course.objects.all()
for c in courses:
    print(c.teacher.username)  # query baru per course!

# Optimized: 1 query
courses = Course.objects.select_related('teacher').all()
```

### 5. Benchmark Perbandingan (30 poin)

Endpoint perbandingan langsung (cek di Swagger `/api/v2/docs`):

| Endpoint | Sebelum | Sesudah | Improvement |
|----------|---------|---------|-------------|
| Course List | N+1 queries | 1 query (select_related) | ~90% |
| Course Members | N+1 queries | 2 queries (prefetch_related) | ~85% |
| Course Dashboard | 3N+1 queries | 1 query (annotate) | ~95% |

### File Terkait
- [`code/courses/apiv2.py`](../code/courses/apiv2.py) — endpoint lab baseline vs optimized
- [`code/courses/apiv1.py`](../code/courses/apiv1.py) — endpoint production (sudah optimized)
- [`code/lms/settings.py`](../code/lms/settings.py) — konfigurasi Silk
- [`code/benchmark.py`](../code/benchmark.py) — script benchmark
