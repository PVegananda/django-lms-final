# Tugas 11: Integrasi Redis ke Simple LMS

## Ketentuan Tugas
1. Setup dan Konfigurasi — 20 poin
2. Implementasi Caching (Cache-Aside + Invalidation) — 40 poin
3. Leaderboard dengan Sorted Set — 20 poin
4. Benchmark dan Monitoring — 20 poin

## Implementasi di Project Ini

### 1. Setup dan Konfigurasi (20 poin)

**Redis service** di [`docker-compose.yml`](../docker-compose.yml):
```yaml
redis:
  image: redis:7-alpine
  container_name: lms-redis
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

**django-redis** di [`code/lms/settings.py`](../code/lms/settings.py):
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "lms",
        "TIMEOUT": 300,
    }
}
```

**Session backend** pakai Redis:
```python
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

Verifikasi:
```bash
docker compose exec redis redis-cli ping
# output: PONG
```

### 2. Implementasi Caching (40 poin)

**Cache-Aside pattern** di `GET /api/v1/courses/{id}`:
```python
cache_key = f'course_detail:{id}'
cached = cache.get(cache_key)
if cached is not None:
    return cached  # cache hit — langsung return

# cache miss — query database
result = Course.objects.prefetch_related('coursecontent_set') \
    .select_related('teacher').get(pk=id)
cache.set(cache_key, result, timeout=300)  # simpan 5 menit
return result
```

**Cache invalidation** saat write operation:
```python
# Di create_course, update_course, delete_course:
cache.delete('courses_list')
cache.delete(f'course_detail:{id}')
```

**Cache monitoring endpoint** (tambahan Final Project):
- `GET /api/v1/cache/status/` — lihat semua keys aktif + TTL
- `DELETE /api/v1/cache/clear/` — bersihkan cache manual

### 3. Leaderboard — Redis Sorted Set (20 poin)

File: [`code/utils/redis_client.py`](../code/utils/redis_client.py)

Menggunakan Redis Sorted Set (ZSET) untuk ranking course:
```python
# Inkremen score saat enrollment baru
update_course_popularity(course_id, score_increment=1)

# Ambil top 10 course
top = get_top_courses(limit=10)
```

Endpoint: `GET /api/v1/courses/popular/`
- Menampilkan top 10 course berdasarkan jumlah enrollment
- Data real-time dari Redis ZREVRANGE

### 4. Benchmark dan Monitoring (20 poin)

**Session tracking** — kunjungan course dicatat di Redis session:
- `POST /api/v1/courses/{id}/visit/` — catat kunjungan
- `GET /api/v1/my-history/` — lihat histori kunjungan

**Redis DB allocation**:
| DB | Kegunaan |
|----|----------|
| DB 0 | Leaderboard (Sorted Set) |
| DB 1 | Cache + Session |
| DB 2 | Celery Result Backend |

### File Terkait
- [`code/utils/redis_client.py`](../code/utils/redis_client.py) — Redis helper functions
- [`code/courses/apiv1.py`](../code/courses/apiv1.py) — caching + session + leaderboard endpoints
- [`code/lms/settings.py`](../code/lms/settings.py) — Redis config
- [`docker-compose.yml`](../docker-compose.yml) — Redis service
