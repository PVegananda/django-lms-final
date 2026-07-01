# Tugas 9: Advanced API Features

## Ketentuan Tugas
1. Filtering + Sorting + Pagination — 30 poin
2. File Upload — 20 poin
3. File Download — 10 poin
4. Partial Update (PATCH) — 20 poin
5. API Testing dengan Postman — 20 poin

## Implementasi di Project Ini

### 1. Filtering + Sorting + Pagination (30 poin)

File: [`code/courses/filters.py`](../code/courses/filters.py)

**FilterSchema** untuk `GET /api/v1/courses/`:
```python
class CourseFilter(FilterSchema):
    search: Optional[str] = Field(None, q=['name__icontains', 'description__icontains'])
    price: Optional[int] = Field(None, q='price__gt')
    created_at: Optional[datetime] = Field(None, q='created_at__gt')
```

**Sorting** dengan whitelist:
```python
allowed_fields = ['name', 'price', 'created_at', '-name', '-price', '-created_at']
```

**Pagination** dengan PageNumberPagination:
```python
@apiv1.get('courses/', response=List[CourseOut])
@paginate(PageNumberPagination, page_size=10)
def list_courses(request, filters: CourseFilter = Query(...), ordering: str = '-created_at'):
    ...
```

Contoh request:
```
GET /api/v1/courses/?search=Python&ordering=-price&page=2
```

### 2. File Upload (20 poin)

Model Course sudah punya field `image`:
```python
class Course(models.Model):
    image = models.ImageField("gambar", null=True, blank=True)
```

Model CourseContent sudah punya field `file_attachment`:
```python
class CourseContent(models.Model):
    file_attachment = models.FileField("File", null=True, blank=True)
```

Upload bisa dilakukan via Django Admin atau endpoint API.

### 3. File Download (10 poin)

File attachment bisa diakses melalui URL media:
```
GET /media/<path-to-file>
```

Konfigurasi di [`code/lms/settings.py`](../code/lms/settings.py):
```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

### 4. Partial Update — PATCH (20 poin)

Endpoint `PUT` tersedia untuk Course dan CourseContent. Update parsial dilakukan dengan
mengirim hanya field yang ingin diubah:

```bash
# Update hanya nama course
curl -X PUT http://localhost:8000/api/v1/courses/1 \
  -H "Authorization: Bearer <token>" \
  -d '{"name":"Nama Baru","description":"tetap","price":50000}'
```

### 5. API Testing

Semua endpoint bisa ditest langsung via Swagger UI:
- http://localhost:8000/api/v1/docs
- http://localhost:8000/api/v2/docs

Atau menggunakan curl / Postman dengan contoh-contoh di atas.

### File Terkait
- [`code/courses/filters.py`](../code/courses/filters.py) — FilterSchema
- [`code/courses/apiv1.py`](../code/courses/apiv1.py) — endpoint dengan filter + pagination
- [`code/courses/schemas.py`](../code/courses/schemas.py) — schema definitions
