# courses/management/commands/import_from_simplelms.py
"""
Management command untuk menyatukan data dari project SimpleLMS (project awal)
ke project Django Ninja (project lanjutan).

Project SimpleLMS adalah proyek latihan awal (modul 01-08) berbasis Django biasa.
Project Django Ninja adalah proyek lanjutan (modul 09-12) dengan REST API + Redis + MongoDB + Celery.

Cara pakai:
    docker compose exec app python manage.py import_from_simplelms
    docker compose exec app python manage.py import_from_simplelms --dry-run
    docker compose exec app python manage.py import_from_simplelms --password admin123
"""
import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Import data dari SimpleLMS (project awal) ke Django Ninja (project lanjutan)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview tanpa menyimpan ke database'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='password123',
            help='Password default untuk semua user yang dibuat (default: password123)'
        )
        parser.add_argument(
            '--fixtures-dir',
            type=str,
            default=None,
            help='Path ke folder fixtures (default: otomatis ditemukan)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        password = options['password']

        # ─── Find fixtures dir ───────────────────────────────────────────────
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )))
        fixtures_dir = options['fixtures_dir'] or os.path.join(base_dir, 'fixtures')

        courses_csv = os.path.join(fixtures_dir, 'simplelms_courses.csv')
        members_csv = os.path.join(fixtures_dir, 'simplelms_members.csv')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🔗 SimpleLMS → Django Ninja Data Merger'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠  DRY RUN MODE — tidak ada perubahan ke database'))
        self.stdout.write('')

        if not os.path.exists(courses_csv):
            self.stdout.write(self.style.ERROR(f'❌ File tidak ditemukan: {courses_csv}'))
            return
        if not os.path.exists(members_csv):
            self.stdout.write(self.style.ERROR(f'❌ File tidak ditemukan: {members_csv}'))
            return

        stats = {
            'users_created': 0,
            'users_exist': 0,
            'courses_created': 0,
            'courses_exist': 0,
            'members_created': 0,
            'members_exist': 0,
        }

        # ─── Step 1: Import Courses (+ Teacher Users) ────────────────────────
        self.stdout.write('📚 Step 1: Import Courses dari SimpleLMS')
        self.stdout.write('-' * 40)

        from courses.models import Course

        with open(courses_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                teacher_username = row['teacher_username'].strip()
                course_name = row['name'].strip()

                # Create/get teacher
                teacher, created = self._get_or_create_user(
                    teacher_username, password, dry_run,
                    first_name=teacher_username.replace('dosen', 'Dosen '),
                    email=f'{teacher_username}@univ.ac.id'
                )
                if created:
                    stats['users_created'] += 1
                    self.stdout.write(f'  👤 Buat user: {teacher_username}')
                else:
                    stats['users_exist'] += 1

                # Create/get course
                if not dry_run:
                    course, created = Course.objects.get_or_create(
                        name=course_name,
                        defaults={
                            'description': row.get('description', '').strip(),
                            'price': int(row.get('price', 0)),
                            'teacher': teacher,
                        }
                    )
                    if created:
                        stats['courses_created'] += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ Course baru: "{course_name}" (by {teacher_username})')
                        )
                    else:
                        stats['courses_exist'] += 1
                        self.stdout.write(f'  ℹ  Course sudah ada: "{course_name}"')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  [DRY] Akan buat course: "{course_name}" (by {teacher_username})')
                    )
                    stats['courses_created'] += 1

        # ─── Step 2: Import Members (+ Student Users) ────────────────────────
        self.stdout.write('')
        self.stdout.write('👥 Step 2: Import Members dari SimpleLMS')
        self.stdout.write('-' * 40)

        from courses.models import Course, CourseMember

        with open(members_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                username = row['username'].strip()
                course_name = row['course_name'].strip()
                roles = row['roles'].strip()

                # Create/get student/assistant user
                user, created = self._get_or_create_user(
                    username, password, dry_run,
                    first_name=username.replace('siswa', 'Mahasiswa ').replace('asisten', 'Asisten '),
                    email=f'{username}@student.ac.id'
                )
                if created:
                    stats['users_created'] += 1
                    self.stdout.write(f'  👤 Buat user: {username}')
                else:
                    stats['users_exist'] += 1

                # Create/get membership
                if not dry_run:
                    try:
                        course = Course.objects.get(name=course_name)
                        member, created = CourseMember.objects.get_or_create(
                            course_id=course,
                            user_id=user,
                            defaults={'roles': roles}
                        )
                        if created:
                            stats['members_created'] += 1
                            role_label = '📖 Siswa' if roles == 'std' else '🎓 Asisten'
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✅ {role_label} {username} → "{course_name}"'
                                )
                            )
                        else:
                            stats['members_exist'] += 1
                            self.stdout.write(f'  ℹ  Member sudah ada: {username} → "{course_name}"')
                    except Course.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠  Course tidak ditemukan: "{course_name}" (skip)')
                        )
                else:
                    role_label = '📖 Siswa' if roles == 'std' else '🎓 Asisten'
                    self.stdout.write(
                        self.style.WARNING(f'  [DRY] {role_label} {username} → "{course_name}"')
                    )
                    stats['members_created'] += 1

        # ─── Step 3: Summary ─────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('📊 HASIL IMPORT'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(
            f"  👤 Users  : {stats['users_created']} dibuat, {stats['users_exist']} sudah ada"
        )
        self.stdout.write(
            f"  📚 Courses: {stats['courses_created']} dibuat, {stats['courses_exist']} sudah ada"
        )
        self.stdout.write(
            f"  👥 Members: {stats['members_created']} dibuat, {stats['members_exist']} sudah ada"
        )
        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('⚠  DRY RUN — tidak ada yang disimpan ke database'))
            self.stdout.write(self.style.WARNING('   Jalankan tanpa --dry-run untuk menyimpan.'))
        else:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ Import dari SimpleLMS selesai!'))
            self.stdout.write('')
            self.stdout.write('Data bisa dicek di:')
            self.stdout.write('  GET http://localhost:8000/api/v1/courses/')
            self.stdout.write('  GET http://localhost:8000/api/analytics/stats/popular-courses/')
        self.stdout.write('')

    def _get_or_create_user(self, username, password, dry_run, first_name='', email=''):
        """Helper: get or create user, returns (user, created)."""
        try:
            user = User.objects.get(username=username)
            return user, False
        except User.DoesNotExist:
            if not dry_run:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    email=email,
                )
                return user, True
            else:
                # In dry-run, return a mock-like result
                return type('FakeUser', (), {'username': username})(), True
