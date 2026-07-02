"""
Automated Tests untuk Django LMS Final Project.

Test dibagi menjadi:
- Unit Test Model: validasi model Course, CourseMember, Review, UserProfile
- Integration Test Auth: register, login, akses dengan/tanpa token
- Integration Test Course CRUD: buat, baca, update, hapus course
- Integration Test Enrollment & Progress: enroll, update progress
- Integration Test Review: buat, lihat, update, hapus review
- Test Permission/RBAC: akses tanpa token (401), aksi tanpa izin (403)

Jalankan:
    docker compose exec app python manage.py test courses -v 2
    docker compose exec app python manage.py test courses --settings=lms.settings_test -v 2
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from courses.models import (
    Course, CourseMember, CourseContent, Comment,
    Category, Review, Progress, UserProfile
)
import json


# =============================================================================
# Helper: base class untuk test yang butuh user dan token
# =============================================================================

class LMSTestCase(TestCase):
    """Base test case dengan helper untuk login dan request authenticated."""

    def setUp(self):
        """Buat user dasar untuk testing."""
        # Instructor
        self.instructor = User.objects.create_user(
            username='test_dosen',
            password='test123',
            email='dosen@test.ac.id',
            first_name='Test',
            last_name='Dosen'
        )
        # Set role instructor
        profile = self.instructor.profile
        profile.role = 'instructor'
        profile.save()

        # Student
        self.student = User.objects.create_user(
            username='test_siswa',
            password='test123',
            email='siswa@test.ac.id',
            first_name='Test',
            last_name='Siswa'
        )

        # Admin
        self.admin = User.objects.create_superuser(
            username='test_admin',
            password='test123',
            email='admin@test.ac.id'
        )

        # Category
        self.category = Category.objects.create(
            name='Pemrograman',
            description='Mata kuliah pemrograman'
        )

        # Course
        self.course = Course.objects.create(
            name='Pemrograman Web',
            description='Belajar web development',
            price=100000,
            teacher=self.instructor,
            category=self.category,
        )

        # Content
        self.content = CourseContent.objects.create(
            name='Pengantar HTML',
            description='Dasar-dasar HTML',
            course_id=self.course,
        )

        self.client = Client()

    def get_token(self, username='test_dosen', password='test123'):
        """Login dan dapatkan JWT access token."""
        response = self.client.post(
            '/api/v1/auth/sign-in',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('access', data.get('token', ''))
        return ''

    def auth_header(self, username='test_dosen', password='test123'):
        """Dapatkan header Authorization untuk request."""
        token = self.get_token(username, password)
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}


# =============================================================================
# 1. UNIT TEST MODEL
# =============================================================================

class TestCourseModel(TestCase):
    """Unit test untuk model Course."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='dosen_test', password='test123', email='d@test.id'
        )
        self.category = Category.objects.create(name='Testing')

    def test_create_course(self):
        """Course bisa dibuat dengan field yang benar."""
        course = Course.objects.create(
            name='Test Course',
            description='Deskripsi test',
            price=50000,
            teacher=self.user,
            category=self.category,
        )
        self.assertEqual(course.name, 'Test Course')
        self.assertEqual(course.price, 50000)
        self.assertEqual(course.teacher, self.user)
        self.assertEqual(course.category, self.category)

    def test_course_str(self):
        """String representation course menampilkan nama."""
        course = Course.objects.create(
            name='Algoritma', teacher=self.user
        )
        self.assertEqual(str(course), 'Algoritma')

    def test_course_default_price(self):
        """Course punya default price 10000."""
        course = Course.objects.create(
            name='Default Price', teacher=self.user
        )
        self.assertEqual(course.price, 10000)

    def test_course_category_nullable(self):
        """Course bisa dibuat tanpa category."""
        course = Course.objects.create(
            name='Tanpa Kategori', teacher=self.user
        )
        self.assertIsNone(course.category)


class TestCourseMemberModel(TestCase):
    """Unit test untuk model CourseMember."""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='dosen_member', password='test123', email='dm@test.id'
        )
        self.student = User.objects.create_user(
            username='siswa_member', password='test123', email='sm@test.id'
        )
        self.course = Course.objects.create(
            name='Test Member', teacher=self.teacher
        )

    def test_enroll_student(self):
        """Student bisa enroll ke course."""
        member = CourseMember.objects.create(
            course_id=self.course,
            user_id=self.student,
            roles='std'
        )
        self.assertEqual(member.roles, 'std')
        self.assertEqual(member.course_id, self.course)

    def test_default_role_is_student(self):
        """Default role member adalah std (siswa)."""
        member = CourseMember.objects.create(
            course_id=self.course,
            user_id=self.student,
        )
        self.assertEqual(member.roles, 'std')

    def test_role_asisten(self):
        """Member bisa punya role asisten."""
        member = CourseMember.objects.create(
            course_id=self.course,
            user_id=self.student,
            roles='ast'
        )
        self.assertEqual(member.roles, 'ast')


class TestReviewModel(TestCase):
    """Unit test untuk model Review."""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='dosen_review', password='test123', email='dr@test.id'
        )
        self.student = User.objects.create_user(
            username='siswa_review', password='test123', email='sr@test.id'
        )
        self.course = Course.objects.create(
            name='Test Review', teacher=self.teacher
        )

    def test_create_review(self):
        """Review bisa dibuat dengan rating 1-5."""
        review = Review.objects.create(
            user=self.student,
            course=self.course,
            rating=4,
            comment='Bagus sekali'
        )
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, 'Bagus sekali')

    def test_unique_user_course_review(self):
        """Satu user hanya bisa kasih satu review per course."""
        Review.objects.create(
            user=self.student, course=self.course, rating=5
        )
        with self.assertRaises(Exception):
            Review.objects.create(
                user=self.student, course=self.course, rating=3
            )

    def test_review_str(self):
        """String representation review menampilkan info yang benar."""
        review = Review.objects.create(
            user=self.student, course=self.course, rating=5
        )
        self.assertIn('siswa_review', str(review))
        self.assertIn('Test Review', str(review))


class TestUserProfileModel(TestCase):
    """Unit test untuk model UserProfile."""

    def test_auto_create_profile(self):
        """Profile otomatis dibuat saat user baru dibuat (via signal)."""
        user = User.objects.create_user(
            username='auto_profile', password='test123', email='ap@test.id'
        )
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'student')

    def test_superuser_gets_admin_role(self):
        """Superuser otomatis mendapat role admin."""
        admin = User.objects.create_superuser(
            username='auto_admin', password='test123', email='aa@test.id'
        )
        self.assertEqual(admin.profile.role, 'admin')

    def test_profile_str(self):
        """String representation profile menampilkan username dan role."""
        user = User.objects.create_user(
            username='profile_str', password='test123', email='ps@test.id'
        )
        self.assertIn('profile_str', str(user.profile))
        self.assertIn('student', str(user.profile))


class TestCategoryModel(TestCase):
    """Unit test untuk model Category."""

    def test_create_category(self):
        """Category bisa dibuat."""
        cat = Category.objects.create(
            name='Test Category', description='Deskripsi'
        )
        self.assertEqual(cat.name, 'Test Category')

    def test_unique_name(self):
        """Nama category harus unik."""
        Category.objects.create(name='Unik')
        with self.assertRaises(Exception):
            Category.objects.create(name='Unik')


# =============================================================================
# 2. INTEGRATION TEST - AUTH
# =============================================================================

class TestAuthEndpoints(LMSTestCase):
    """Integration test untuk endpoint authentication."""

    def test_register_success(self):
        """User baru bisa register."""
        response = self.client.post(
            '/api/v1/register/',
            data=json.dumps({
                'username': 'baru',
                'password': 'pass123',
                'email': 'baru@test.id',
                'first_name': 'User',
                'last_name': 'Baru'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['username'], 'baru')

    def test_register_duplicate_username(self):
        """Register dengan username yang sudah ada harus gagal."""
        response = self.client.post(
            '/api/v1/register/',
            data=json.dumps({
                'username': 'test_dosen',  # sudah ada
                'password': 'pass123',
                'email': 'baru2@test.id',
                'first_name': 'A',
                'last_name': 'B'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        """Login dengan credential yang benar mengembalikan token."""
        response = self.client.post(
            '/api/v1/auth/sign-in',
            data=json.dumps({
                'username': 'test_dosen',
                'password': 'test123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access', data)

    def test_login_wrong_password(self):
        """Login dengan password salah harus gagal."""
        response = self.client.post(
            '/api/v1/auth/sign-in',
            data=json.dumps({
                'username': 'test_dosen',
                'password': 'salah'
            }),
            content_type='application/json'
        )
        self.assertNotEqual(response.status_code, 200)


# =============================================================================
# 3. INTEGRATION TEST - COURSE CRUD
# =============================================================================

class TestCourseCRUD(LMSTestCase):
    """Integration test untuk endpoint Course CRUD."""

    def test_list_courses(self):
        """GET /courses/ mengembalikan list course."""
        response = self.client.get('/api/v1/courses/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('items', data)

    def test_get_course_detail(self):
        """GET /courses/{id} mengembalikan detail course."""
        response = self.client.get(f'/api/v1/courses/{self.course.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'Pemrograman Web')

    def test_get_course_not_found(self):
        """GET /courses/99999 mengembalikan 404."""
        response = self.client.get('/api/v1/courses/99999')
        self.assertEqual(response.status_code, 404)

    def test_create_course_authenticated(self):
        """POST /courses/ dengan token mengembalikan course baru."""
        response = self.client.post(
            '/api/v1/courses/',
            data=json.dumps({
                'name': 'Course Baru',
                'description': 'Deskripsi baru',
                'price': 75000
            }),
            content_type='application/json',
            **self.auth_header()
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'Course Baru')

    def test_create_course_unauthenticated(self):
        """POST /courses/ tanpa token mengembalikan 401."""
        response = self.client.post(
            '/api/v1/courses/',
            data=json.dumps({
                'name': 'Gagal',
                'description': 'Tanpa token'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_update_course_by_owner(self):
        """PUT /courses/{id} oleh owner berhasil."""
        response = self.client.put(
            f'/api/v1/courses/{self.course.id}',
            data=json.dumps({
                'name': 'Updated Course',
                'description': 'Updated',
                'price': 200000
            }),
            content_type='application/json',
            **self.auth_header()
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Updated Course')

    def test_update_course_by_non_owner(self):
        """PUT /courses/{id} oleh bukan owner mengembalikan 403."""
        response = self.client.put(
            f'/api/v1/courses/{self.course.id}',
            data=json.dumps({
                'name': 'Hijack',
                'description': 'Coba ubah',
                'price': 1
            }),
            content_type='application/json',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_course_by_owner(self):
        """DELETE /courses/{id} oleh owner berhasil."""
        # Buat course baru dulu supaya tidak ganggu test lain
        course = Course.objects.create(
            name='Hapus Ini', teacher=self.instructor
        )
        response = self.client.delete(
            f'/api/v1/courses/{course.id}',
            **self.auth_header()
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_course_by_non_owner(self):
        """DELETE /courses/{id} oleh bukan owner mengembalikan 403."""
        response = self.client.delete(
            f'/api/v1/courses/{self.course.id}',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 403)

    def test_search_courses(self):
        """GET /courses/?search=web mencari course berdasarkan nama."""
        response = self.client.get('/api/v1/courses/?search=web')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data['items']) > 0)

    def test_filter_by_category(self):
        """GET /courses/?category_id= memfilter berdasarkan kategori."""
        response = self.client.get(
            f'/api/v1/courses/?category_id={self.category.id}'
        )
        self.assertEqual(response.status_code, 200)

    def test_filter_by_instructor(self):
        """GET /courses/?instructor= memfilter berdasarkan username dosen."""
        response = self.client.get('/api/v1/courses/?instructor=test_dosen')
        self.assertEqual(response.status_code, 200)


# =============================================================================
# 4. INTEGRATION TEST - ENROLLMENT & PROGRESS
# =============================================================================

class TestEnrollmentProgress(LMSTestCase):
    """Integration test untuk endpoint enrollment dan progress."""

    def test_enroll_success(self):
        """POST /course/{id}/enroll/ berhasil untuk user yang belum enrolled."""
        response = self.client.post(
            f'/api/v1/course/{self.course.id}/enroll/',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 200)

    def test_enroll_duplicate(self):
        """POST /course/{id}/enroll/ kedua kalinya mengembalikan 400."""
        # Enroll pertama
        CourseMember.objects.create(
            course_id=self.course, user_id=self.student, roles='std'
        )
        response = self.client.post(
            f'/api/v1/course/{self.course.id}/enroll/',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 400)

    def test_my_courses(self):
        """GET /mycourses/ mengembalikan course yang diikuti."""
        CourseMember.objects.create(
            course_id=self.course, user_id=self.student, roles='std'
        )
        response = self.client.get(
            '/api/v1/mycourses/',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 200)

    def test_update_progress(self):
        """POST /progress/ berhasil untuk enrolled student."""
        CourseMember.objects.create(
            course_id=self.course, user_id=self.student, roles='std'
        )
        response = self.client.post(
            '/api/v1/progress/',
            data=json.dumps({
                'content_id': self.content.id,
                'status': 'in_progress'
            }),
            content_type='application/json',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertIn(response.status_code, [200, 201])

    def test_update_progress_not_enrolled(self):
        """POST /progress/ gagal jika tidak enrolled."""
        response = self.client.post(
            '/api/v1/progress/',
            data=json.dumps({
                'content_id': self.content.id,
                'status': 'in_progress'
            }),
            content_type='application/json',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 403)

    def test_my_progress(self):
        """GET /progress/my/ mengembalikan progress student."""
        response = self.client.get(
            '/api/v1/progress/my/',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 200)


# =============================================================================
# 5. INTEGRATION TEST - REVIEW
# =============================================================================

class TestReviewEndpoints(LMSTestCase):
    """Integration test untuk endpoint Review."""

    def setUp(self):
        super().setUp()
        # Enroll student supaya bisa review
        CourseMember.objects.create(
            course_id=self.course, user_id=self.student, roles='std'
        )

    def test_create_review(self):
        """POST /reviews/ berhasil untuk enrolled student."""
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps({
                'course_id': self.course.id,
                'rating': 5,
                'comment': 'Sangat bagus!'
            }),
            content_type='application/json',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 201)

    def test_create_review_not_enrolled(self):
        """POST /reviews/ gagal untuk user yang tidak enrolled."""
        # Buat student baru yang tidak enrolled
        other = User.objects.create_user(
            username='outsider', password='test123', email='out@test.id'
        )
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps({
                'course_id': self.course.id,
                'rating': 3,
                'comment': 'Coba review'
            }),
            content_type='application/json',
            **self.auth_header('outsider', 'test123')
        )
        self.assertEqual(response.status_code, 403)

    def test_create_review_duplicate(self):
        """POST /reviews/ kedua kalinya mengembalikan 400."""
        Review.objects.create(
            user=self.student, course=self.course, rating=4
        )
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps({
                'course_id': self.course.id,
                'rating': 5,
                'comment': 'Review kedua'
            }),
            content_type='application/json',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_rating(self):
        """POST /reviews/ dengan rating > 5 gagal validasi."""
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps({
                'course_id': self.course.id,
                'rating': 10,
                'comment': 'Rating salah'
            }),
            content_type='application/json',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 422)

    def test_list_course_reviews(self):
        """GET /reviews/course/{id}/ menampilkan review + rata-rata rating."""
        Review.objects.create(
            user=self.student, course=self.course, rating=4, comment='OK'
        )
        response = self.client.get(
            f'/api/v1/reviews/course/{self.course.id}/'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_reviews'], 1)
        self.assertEqual(data['average_rating'], 4.0)

    def test_delete_review_by_owner(self):
        """DELETE /reviews/{id}/ oleh pemilik review berhasil."""
        review = Review.objects.create(
            user=self.student, course=self.course, rating=3
        )
        response = self.client.delete(
            f'/api/v1/reviews/{review.id}/',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_review_by_non_owner(self):
        """DELETE /reviews/{id}/ oleh bukan pemilik mengembalikan 403."""
        review = Review.objects.create(
            user=self.student, course=self.course, rating=3
        )
        response = self.client.delete(
            f'/api/v1/reviews/{review.id}/',
            **self.auth_header('test_dosen', 'test123')
        )
        self.assertEqual(response.status_code, 403)


# =============================================================================
# 6. INTEGRATION TEST - DASHBOARD
# =============================================================================

class TestDashboard(LMSTestCase):
    """Integration test untuk endpoint dashboard mahasiswa."""

    def test_dashboard_success(self):
        """GET /dashboard/ mengembalikan data ringkasan."""
        response = self.client.get(
            '/api/v1/dashboard/',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('user', data)
        self.assertIn('enrolled_courses', data)
        self.assertIn('progress', data)
        self.assertIn('recommendations', data)

    def test_dashboard_unauthenticated(self):
        """GET /dashboard/ tanpa token mengembalikan 401."""
        response = self.client.get('/api/v1/dashboard/')
        self.assertEqual(response.status_code, 401)


# =============================================================================
# 7. TEST PERMISSION / RBAC
# =============================================================================

class TestPermissions(LMSTestCase):
    """Test akses kontrol dan permission."""

    def test_unauthenticated_create_course(self):
        """POST /courses/ tanpa token → 401."""
        response = self.client.post(
            '/api/v1/courses/',
            data=json.dumps({'name': 'X', 'description': 'Y'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_enroll(self):
        """POST /course/{id}/enroll/ tanpa token → 401."""
        response = self.client.post(
            f'/api/v1/course/{self.course.id}/enroll/'
        )
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_progress(self):
        """POST /progress/ tanpa token → 401."""
        response = self.client.post(
            '/api/v1/progress/',
            data=json.dumps({'content_id': 1, 'status': 'completed'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_review(self):
        """POST /reviews/ tanpa token → 401."""
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps({'course_id': 1, 'rating': 5}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_dashboard(self):
        """GET /dashboard/ tanpa token → 401."""
        response = self.client.get('/api/v1/dashboard/')
        self.assertEqual(response.status_code, 401)

    def test_non_owner_update_course(self):
        """PUT /courses/{id} oleh bukan owner → 403."""
        response = self.client.put(
            f'/api/v1/courses/{self.course.id}',
            data=json.dumps({
                'name': 'Hijack', 'description': 'X', 'price': 1
            }),
            content_type='application/json',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 403)

    def test_non_owner_delete_course(self):
        """DELETE /courses/{id} oleh bukan owner (dan bukan admin) → 403."""
        response = self.client.delete(
            f'/api/v1/courses/{self.course.id}',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_delete_any_course(self):
        """DELETE /courses/{id} oleh admin berhasil."""
        course = Course.objects.create(
            name='Admin Delete', teacher=self.instructor
        )
        response = self.client.delete(
            f'/api/v1/courses/{course.id}',
            **self.auth_header('test_admin', 'test123')
        )
        self.assertEqual(response.status_code, 204)

    def test_non_enrolled_comment(self):
        """POST /comments/ oleh user yang tidak enrolled → 403."""
        response = self.client.post(
            '/api/v1/comments/',
            data=json.dumps({
                'comment': 'Coba komentar',
                'content_id': self.content.id
            }),
            content_type='application/json',
            **self.auth_header('test_siswa', 'test123')
        )
        self.assertEqual(response.status_code, 403)

    def test_category_public_access(self):
        """GET /categories/ bisa diakses tanpa login."""
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(response.status_code, 200)

    def test_hello_endpoint(self):
        """GET /hello/ mengembalikan response tanpa auth."""
        response = self.client.get('/api/v1/hello/')
        self.assertEqual(response.status_code, 200)
