# Tugas 10: Automated Testing

## Ketentuan Tugas
1. Unit Testing (minimal 5 test model + 5 test utilitas) — 30 poin
2. Integration Testing (minimal 3 endpoint + 3 negatif) — 40 poin
3. Test Coverage (minimal 80%) — 20 poin
4. Load Testing dengan Locust — 10 poin

## Implementasi di Project Ini

### 1. Unit Testing (30 poin)

File: [`code/courses/tests.py`](../code/courses/tests.py)

Test yang tersedia:
- Model creation test (Course, CourseMember, CourseContent)
- Validator test (harga negatif, duplikasi username)
- Helper function test (get_object_or_404)
- Schema validation test (ProgressIn status check)
- Model string representation test

Jalankan unit test:
```bash
docker compose exec app python manage.py test courses -v 2
```

### 2. Integration Testing (40 poin)

Test endpoint API:
- **Course CRUD**: GET list, POST create, PUT update, DELETE
- **Enrollment**: POST enroll, GET mycourses
- **Comment**: POST create (harus enrolled), DELETE (pemilik/teacher/admin)
- **Negatif**: akses tanpa token (401), aksi tanpa izin (403), resource tidak ada (404)

```bash
docker compose exec app python manage.py test courses.tests -v 2
```

### 3. Test Coverage (20 poin)

Jalankan test dengan coverage:
```bash
docker compose exec app coverage run manage.py test courses
docker compose exec app coverage report
docker compose exec app coverage html  # buat laporan HTML
```

Konfigurasi test terpisah di [`code/lms/settings_test.py`](../code/lms/settings_test.py)
yang menggunakan SQLite dan skip Silk untuk mempercepat test.

### 4. Load Testing — Locust (10 poin)

Load test tersedia via Locust yang sudah ada di `requirements.txt`:
```bash
# Jalankan locust
docker compose exec app locust -f benchmark.py --headless -u 10 -r 2 -t 30s --host http://localhost:8000
```

File: [`code/benchmark.py`](../code/benchmark.py)

Task yang ditest:
- GET /api/v1/courses/ — list courses
- GET /api/v1/courses/{id} — detail course
- POST /api/v1/courses/ — create course (authenticated)

### File Terkait
- [`code/courses/tests.py`](../code/courses/tests.py) — test cases
- [`code/lms/settings_test.py`](../code/lms/settings_test.py) — test settings
- [`code/benchmark.py`](../code/benchmark.py) — locust load test
- [`code/requirements.txt`](../code/requirements.txt) — `coverage` dan `locust`
