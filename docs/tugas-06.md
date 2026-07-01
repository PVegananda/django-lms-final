# Tugas 6: REST API untuk Simple LMS

## Ketentuan Tugas
1. Setup Django Ninja — 10 poin
2. Schema Definition (minimal 4 schema) — 15 poin
3. CRUD Endpoints Course — 25 poin
4. CRUD Endpoints CourseContent — 25 poin
5. Error Handling dan Query Parameters — 15 poin
6. Testing dan Dokumentasi — 10 poin

## Implementasi di Project Ini

### 1. Setup Django Ninja (10 poin)

File: [`code/courses/apiv1.py`](../code/courses/apiv1.py)

```python
from ninja import NinjaAPI

apiv1 = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
    description="REST API untuk Simple Learning Management System"
)
```

Registrasi di URL: [`code/lms/urls.py`](../code/lms/urls.py)
```python
urlpatterns = [
    path("api/v1/", apiv1.urls),
    path("api/v2/", apiv2.urls),
    path("api/analytics/", analytics_api.urls),
]
```

Swagger UI: http://localhost:8000/api/v1/docs

### 2. Schema Definition (15 poin)

File: [`code/courses/schemas.py`](../code/courses/schemas.py)

| Schema | Tipe | Keterangan |
|--------|------|------------|
| `CourseIn` | Input | name, description, price |
| `CourseOut` | Output | + id, teacher (nested), timestamps |
| `DetailCourseOut` | Output | + contents list |
| `CourseContentIn` | Input | name, description, video_url, course_id, parent_id |
| `CourseContentOut` | Output | + id, timestamps |
| `UserOut` | Output | id, username, first_name, last_name, email |
| `Register` | Input | username, password, email, first/last name |
| `CommentIn` | Input | comment, content_id |
| `ProgressIn` | Input | content_id, status |
| `CategoryOut` | Output | id, name, description |

### 3. CRUD Endpoints Course (25 poin)

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/v1/courses/` | List dengan filter, sort, pagination |
| GET | `/api/v1/courses/{id}` | Detail course + konten |
| POST | `/api/v1/courses/` | Buat course baru (auth) |
| PUT | `/api/v1/courses/{id}` | Update course (owner only) |
| DELETE | `/api/v1/courses/{id}` | Hapus course (owner/admin) |

### 4. CRUD Endpoints CourseContent (25 poin)

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/v1/contents/` | List + filter by course_id |
| GET | `/api/v1/contents/{id}` | Detail konten |
| POST | `/api/v1/contents/` | Buat konten (teacher only) |
| PUT | `/api/v1/contents/{id}` | Update konten (teacher only) |
| DELETE | `/api/v1/contents/{id}` | Hapus konten (teacher/admin) |

### 5. Error Handling (15 poin)

Helper function `get_object_or_404`:
```python
def get_object_or_404(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise HttpError(404, f"{model.__name__} tidak ditemukan")
```

Error codes yang digunakan:
- `400` — validasi gagal (harga negatif, duplikasi, dll)
- `401` — tidak ada token
- `403` — tidak punya izin
- `404` — data tidak ditemukan

Query parameters di `GET /courses/`:
- `?search=` — cari nama/deskripsi
- `?ordering=` — sort by name, price, created_at
- `?page=` — pagination (10 per halaman)

### 6. Swagger UI
Semua endpoint terdokumentasi otomatis lengkap dengan:
- Docstring per endpoint
- Request/response schema
- Try-it-out untuk testing langsung

### File Terkait
- [`code/courses/apiv1.py`](../code/courses/apiv1.py) — semua endpoint
- [`code/courses/schemas.py`](../code/courses/schemas.py) — semua schema
- [`code/courses/filters.py`](../code/courses/filters.py) — filter classes
- [`code/lms/urls.py`](../code/lms/urls.py) — URL routing
