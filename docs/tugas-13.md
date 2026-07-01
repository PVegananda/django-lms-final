# Tugas 13: Message Brokers — Celery + RabbitMQ

## Ketentuan Tugas
1. Setup Infrastructure (RabbitMQ, Celery Worker, Celery Beat, Flower) — 20 poin
2. Background Tasks (minimal 3 Celery task) — 30 poin
3. Periodic Tasks — 20 poin
4. Error Handling (retry, chaining) — 15 poin
5. Monitoring dan Dokumentasi — 15 poin

## Implementasi di Project Ini

### 1. Setup Infrastructure (20 poin)

Semua service sudah berjalan di [`docker-compose.yml`](../docker-compose.yml):

```yaml
# RabbitMQ — message broker
rabbitmq:
  image: rabbitmq:3-management-alpine
  ports:
    - "5672:5672"      # AMQP
    - "15672:15672"    # Management UI
  environment:
    RABBITMQ_DEFAULT_USER: admin
    RABBITMQ_DEFAULT_PASS: password123
  healthcheck:
    test: rabbitmq-diagnostics -q ping

# Celery Worker — eksekusi task
celery_worker:
  build: .
  command: celery -A lms worker -l info
  depends_on: [app, rabbitmq, redis]

# Celery Beat — jadwal periodic task
celery_beat:
  build: .
  command: celery -A lms beat -l info
  depends_on: [celery_worker]
```

**Celery config** di [`code/lms/celery.py`](../code/lms/celery.py):
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
app = Celery('lms')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**Settings** di [`code/lms/settings.py`](../code/lms/settings.py):
```python
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://admin:password123@rabbitmq:5672//')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', f'{REDIS_URL}/2')
```

Verifikasi semua service:
```bash
docker compose ps
# rabbitmq, celery_worker, celery_beat semuanya Up
```

RabbitMQ Management UI: http://localhost:15672/ (admin/password123)

### 2. Background Tasks (30 poin)

File: [`code/courses/tasks.py`](../code/courses/tasks.py)

**Task 1 — Notifikasi email enrollment:**
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_enrollment_notification(self, user_id, course_id):
    # Kirim email (mock) saat user enroll ke course
    ...
```

Dipanggil di endpoint enroll:
```python
send_enrollment_notification.delay(user.id, course_id)
```

**Task 2 — Generate report course:**
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def generate_course_report(self, course_id):
    # Generate statistik course: total member, content, comments
    # Hasilnya disimpan di Redis result backend
    ...
```

Endpoint trigger:
- `POST /api/v1/reports/generate/{course_id}/` → dapat `task_id`
- `GET /api/v1/reports/status/{task_id}/` → cek status (PENDING → STARTED → SUCCESS)

**Task 3 — Generate daily stats:**
```python
@shared_task
def generate_daily_stats():
    # Statistik harian: total users, courses, members, contents
    ...
```

**Task 4 — Cleanup old logs:**
```python
@shared_task
def cleanup_old_logs():
    # Hapus activity logs MongoDB yang > 30 hari
    ...
```

### 3. Periodic Tasks (20 poin)

Konfigurasi di [`code/lms/settings.py`](../code/lms/settings.py):
```python
CELERY_BEAT_SCHEDULE = {
    # Setiap hari pukul 00:00 — generate statistik harian
    'daily-course-stats': {
        'task': 'courses.tasks.generate_daily_stats',
        'schedule': crontab(hour=0, minute=0),
    },
    # Setiap hari pukul 02:00 — cleanup log lama
    'cleanup-old-activity-logs': {
        'task': 'courses.tasks.cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0),
    },
}
```

Untuk testing bisa ubah schedule sementara ke 30 detik:
```python
'schedule': 30.0,  # setiap 30 detik
```

### 4. Error Handling (15 poin)

**Retry mechanism:**
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_enrollment_notification(self, user_id, course_id):
    try:
        ...
    except Exception as exc:
        raise self.retry(exc=exc)
```

**Silent error di caller** — error Celery tidak merusak API response:
```python
try:
    send_enrollment_notification.delay(user.id, course_id)
except Exception:
    pass  # Celery down? Tidak masalah, user tetap dapat response
```

Settings retry:
```python
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # retry setelah 60 detik
```

### 5. Monitoring (15 poin)

**Task status endpoint:**
```python
@apiv1.get('reports/status/{task_id}/')
def report_status(request, task_id: str):
    result = AsyncResult(task_id)
    return {
        'task_id': task_id,
        'status': result.status,  # PENDING | STARTED | SUCCESS | FAILURE
        'result': result.result if result.ready() else None,
    }
```

**RabbitMQ Management UI:**
- http://localhost:15672/
- Login: admin / password123
- Bisa lihat: queues, connections, channels, message rates

**Monitoring via docker logs:**
```bash
# Lihat log worker
docker compose logs celery_worker -f

# Lihat log beat
docker compose logs celery_beat -f
```

### File Terkait
- [`code/courses/tasks.py`](../code/courses/tasks.py) — semua Celery tasks
- [`code/lms/celery.py`](../code/lms/celery.py) — Celery app config
- [`code/lms/__init__.py`](../code/lms/__init__.py) — Celery app import
- [`code/lms/settings.py`](../code/lms/settings.py) — Celery + Beat config
- [`docker-compose.yml`](../docker-compose.yml) — RabbitMQ, Worker, Beat services
