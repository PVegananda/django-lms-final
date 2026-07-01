# Tugas 7: Authentication & Authorization

## Ketentuan Tugas
1. Setup JWT Authentication — 15 poin
2. User Registration — 15 poin
3. Proteksi Endpoint — 20 poin
4. Authorization Checks — 30 poin
5. Security & Testing — 20 poin

## Implementasi di Project Ini

### 1. Setup JWT Authentication (15 poin)

Menggunakan `ninja-simple-jwt` dengan RSA keys.

Setup di [`code/courses/apiv1.py`](../code/courses/apiv1.py):
```python
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth

apiv1.add_router("/auth/", mobile_auth_router)
apiAuth = HttpJwtAuth()
```

Endpoint auth:
- `POST /api/v1/auth/sign-in` → login, dapat access + refresh token
- `POST /api/v1/auth/token-refresh` → refresh access token

Generate RSA keys:
```bash
docker compose exec app python manage.py make_jwt_key
```

### 2. User Registration (15 poin)

```python
@apiv1.post('register/', response={201: UserOut})
def register(request, data: Register):
    # Cek duplikasi username
    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Username sudah digunakan")
    # Cek duplikasi email
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "Email sudah digunakan")
    # Buat user dengan password hashing otomatis
    new_user = User.objects.create_user(...)
    return 201, new_user
```

Rate limited: 5 request per menit (mencegah brute force).

### 3. Proteksi Endpoint (20 poin)

Endpoint yang dilindungi dengan `auth=apiAuth`:
- `POST /api/v1/courses/` — buat course (harus login)
- `PUT /api/v1/courses/{id}` — update course (harus login + owner)
- `DELETE /api/v1/courses/{id}` — hapus course (harus login + owner/admin)
- `POST /api/v1/course/{id}/enroll/` — daftar ke course (harus login + cek duplikasi)
- `GET /api/v1/mycourses/` — course saya (harus login)
- `POST /api/v1/progress/` — update progress (harus login + harus enrolled)

### 4. Authorization Checks (30 poin)

Semua endpoint sudah punya authorization check:

| Endpoint | Rule | Error |
|----------|------|-------|
| `POST /comments/` | Hanya enrolled user yang bisa komentar | 403 |
| `PUT /comments/{id}` | Hanya pemilik komentar | 403 |
| `DELETE /comments/{id}` | Pemilik komentar ATAU course owner ATAU superadmin | 403 |
| `PUT /courses/{id}` | Hanya course owner | 403 |
| `DELETE /courses/{id}` | Course owner ATAU superadmin | 403 |
| `POST /progress/` | Harus enrolled di course | 403 |
| `GET /progress/course/{id}/` | Hanya teacher course atau admin | 403 |
| `POST /categories/` | Hanya superadmin | 403 |
| `GET /cache/status/` | Hanya superadmin | 403 |

### 5. Security & Testing (20 poin)

Alur lengkap yang bisa di-test via Swagger:

1. **Register** → `POST /api/v1/register/`
2. **Login** → `POST /api/v1/auth/sign-in` → dapat token
3. **Akses dengan token** → klik "Authorize" di Swagger, masukkan `Bearer <token>`
4. **Akses tanpa token** → response 401 Unauthorized
5. **Aksi tidak diizinkan** → misal student coba delete course → 403 Forbidden
6. **Refresh token** → `POST /api/v1/auth/token-refresh`

### File Terkait
- [`code/courses/apiv1.py`](../code/courses/apiv1.py) — semua endpoint + auth
- [`code/courses/schemas.py`](../code/courses/schemas.py) — Register schema
- [`code/lms/settings.py`](../code/lms/settings.py) — JWT config
