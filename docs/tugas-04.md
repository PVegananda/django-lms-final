# Tugas 4: Simple LMS — Model dan Data

## Ketentuan Tugas
1. Setup Model sesuai ERD (Course, CourseMember, CourseContent, Comment) — 40 poin
2. Import Data dari CSV — 20 poin
3. Query CRUD — 20 poin
4. Query Relasional — 20 poin

## Implementasi di Project Ini

### 1. Model (40 poin)

File: [`code/courses/models.py`](../code/courses/models.py)

Model yang dibuat:

| Model | Field Utama | Keterangan |
|-------|-------------|------------|
| `Category` | name, description | Kategori course (tambahan Final Project) |
| `Course` | name, description, price, teacher, category | Mata kuliah |
| `CourseMember` | course_id, user_id, roles | Enrollment (siswa/asisten) |
| `CourseContent` | name, description, video_url, course_id, parent_id | Konten belajar (hierarkis) |
| `Comment` | content_id, user_id, comment | Komentar per konten |
| `Progress` | user, course, content, status | Tracking belajar (tambahan Final Project) |

**Admin Panel** — semua model terdaftar di Django Admin dengan `list_display` dan `search_fields`:
File: [`code/courses/admin.py`](../code/courses/admin.py)

```python
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'category', 'price', 'created_at')
    list_filter = ('teacher', 'category', 'created_at')
    search_fields = ('name', 'description')
```

Akses admin panel: http://localhost:8000/admin/

### 2. Import Data dari CSV (20 poin)

File CSV: [`code/fixtures/simplelms_courses.csv`](../code/fixtures/simplelms_courses.csv) dan [`code/fixtures/simplelms_members.csv`](../code/fixtures/simplelms_members.csv)

Management command untuk import:
File: [`code/courses/management/commands/import_from_simplelms.py`](../code/courses/management/commands/import_from_simplelms.py)

```bash
# Import data dari CSV SimpleLMS
docker compose exec app python manage.py import_from_simplelms
```

Selain CSV, ada juga seed data yang lebih lengkap:
File: [`code/courses/management/commands/seed_data.py`](../code/courses/management/commands/seed_data.py)

```bash
# Seed data utama: 100 courses, 20 teachers, 500 members, dll
docker compose exec app python manage.py seed_data
```

### 3. Query CRUD (20 poin)

Semua operasi CRUD tersedia via REST API:

```bash
# CREATE — buat course baru
curl -X POST http://localhost:8000/api/v1/courses/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Pemrograman Web","description":"Belajar web dev","price":50000}'

# READ — daftar semua course dengan harga di atas 40000
curl "http://localhost:8000/api/v1/courses/?price=40000"

# UPDATE — update course tertentu
curl -X PUT http://localhost:8000/api/v1/courses/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Pemrograman Web Lanjut","description":"Updated","price":75000}'

# DELETE — hapus course
curl -X DELETE http://localhost:8000/api/v1/courses/1 \
  -H "Authorization: Bearer <token>"
```

### 4. Query Relasional (20 poin)

Semua query relasional sudah dioptimasi di endpoint:

- **Course beserta nama pengajar**: `GET /api/v1/courses/` → pakai `select_related('teacher')`
- **Member per course**: `GET /api/v1/course/{id}/enroll/` → pakai filter relasi
- **Jumlah member per course**: `GET /api/v2/lab/course-dashboard/optimized/` → pakai `annotate(Count())`
- **Top 3 course dengan member terbanyak**: `GET /api/v1/courses/popular/` → Redis Sorted Set

### File Terkait
- [`code/courses/models.py`](../code/courses/models.py) — semua model
- [`code/courses/admin.py`](../code/courses/admin.py) — admin panel
- [`code/courses/management/commands/seed_data.py`](../code/courses/management/commands/seed_data.py) — seed data
- [`code/fixtures/`](../code/fixtures/) — CSV data
