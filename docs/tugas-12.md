# Tugas 12: Analytics System dengan MongoDB

## Ketentuan Tugas
1. Setup dan Data Modeling — 20 poin
2. CRUD dan Seed Data — 20 poin
3. Aggregation Pipeline — 25 poin
4. Integrasi Django — 25 poin
5. Indexing — 10 poin

## Implementasi di Project Ini

### 1. Setup dan Data Modeling (20 poin)

**MongoDB service** di [`docker-compose.yml`](../docker-compose.yml):
```yaml
mongodb:
  image: mongo:7
  container_name: lms-mongodb
  environment:
    - MONGO_INITDB_ROOT_USERNAME=admin
    - MONGO_INITDB_ROOT_PASSWORD=password123
  ports:
    - "27017:27017"
  volumes:
    - mongodb_data:/data/db
```

**Document schema** di project ini menggunakan **embedding** untuk data yang sering dibaca
bersamaan:

Collection `activity_logs`:
```json
{
  "user_id": 1,
  "username": "siswa01",
  "action": "view_course",
  "course_id": 5,
  "course_name": "Pemrograman Web",
  "timestamp": "2025-01-15T10:30:00Z",
  "metadata": {"source": "api_v1"}
}
```

Keputusan embedding vs referencing:
- **Embedding** `course_name` di activity log → biar tidak perlu JOIN ke PostgreSQL saat baca
- **Referencing** `user_id` dan `course_id` → karena user/course bisa berubah

### 2. CRUD dan Seed Data (20 poin)

File: [`code/analytics/management/commands/seed_analytics.py`](../code/analytics/management/commands/seed_analytics.py)

```bash
# Seed 200 dokumen activity log realistis
docker compose exec app python manage.py seed_analytics --count 200
```

CRUD operations tersedia via:
- **Insert**: otomatis saat user view course atau enroll (via `log_activity()`)
- **Find**: `GET /api/analytics/stats/` endpoints
- **Update**: via aggregation pipeline
- **Delete**: task `cleanup_old_logs` (hapus log > 30 hari)

### 3. Aggregation Pipeline (25 poin)

File: [`code/analytics/aggregation_service.py`](../code/analytics/aggregation_service.py)

Pipeline yang dibuat:

**1. Ringkasan aksi per tipe:**
```python
pipeline = [
    {"$group": {"_id": "$action", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
```
Endpoint: `GET /api/analytics/stats/action-summary/`

**2. Top active users:**
```python
pipeline = [
    {"$group": {"_id": "$username", "total_actions": {"$sum": 1}}},
    {"$sort": {"total_actions": -1}},
    {"$limit": 10}
]
```
Endpoint: `GET /api/analytics/stats/active-users/`

**3. Course paling populer (by views + unique users):**
```python
pipeline = [
    {"$match": {"action": "view_course"}},
    {"$group": {
        "_id": "$course_name",
        "view_count": {"$sum": 1},
        "unique_users": {"$addToSet": "$username"}
    }},
    {"$addFields": {"unique_user_count": {"$size": "$unique_users"}}},
    {"$sort": {"view_count": -1}},
    {"$limit": 5}
]
```
Endpoint: `GET /api/analytics/stats/popular-courses/`

**4. Statistik harian (7 hari terakhir):**
Endpoint: `GET /api/analytics/stats/daily/`

### 4. Integrasi Django (25 poin)

**Activity Service** — file: [`code/analytics/activity_service.py`](../code/analytics/activity_service.py)

```python
from analytics.activity_service import log_activity, ACTION_VIEW_COURSE, ACTION_ENROLL

# Dipanggil di endpoint view course (silent — tidak blokir response)
try:
    log_activity(
        user_id=user.id, username=user.username,
        action=ACTION_VIEW_COURSE, course_id=id,
        course_name=result.name, metadata={'source': 'api_v1'}
    )
except Exception:
    pass  # MongoDB error tidak merusak response utama
```

**API endpoints** — file: [`code/analytics/api.py`](../code/analytics/api.py):
- `GET /api/analytics/stats/action-summary/`
- `GET /api/analytics/stats/active-users/`
- `GET /api/analytics/stats/popular-courses/`
- `GET /api/analytics/stats/daily/`

Swagger: http://localhost:8000/api/analytics/docs

### 5. Indexing (10 poin)

Index dibuat pada field yang sering di-query:
- `timestamp` — untuk query range (daily stats, cleanup)
- `action` — untuk filter by action type
- `user_id` — untuk query per user

### File Terkait
- [`code/analytics/activity_service.py`](../code/analytics/activity_service.py) — log activity
- [`code/analytics/aggregation_service.py`](../code/analytics/aggregation_service.py) — pipelines
- [`code/analytics/api.py`](../code/analytics/api.py) — analytics endpoints
- [`code/utils/mongo_client.py`](../code/utils/mongo_client.py) — MongoDB client
- [`docker-compose.yml`](../docker-compose.yml) — MongoDB service
