from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# =============================================================================
# UserProfile — role system eksplisit (Final Project)
# =============================================================================

USER_ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('instructor', 'Instructor'),
    ('student', 'Student'),
]


class UserProfile(models.Model):
    """
    Profil tambahan untuk User.
    Setiap user punya satu profile yang menyimpan role dan bio.
    Dibuat otomatis saat user baru di-create lewat signal.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        "peran",
        max_length=10,
        choices=USER_ROLE_CHOICES,
        default='student'
    )
    bio = models.TextField("bio", blank=True, default='')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    class Meta:
        verbose_name = "Profil User"
        verbose_name_plural = "Profil User"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Buat UserProfile otomatis saat User baru dibuat."""
    if created:
        # Jika user adalah superuser, set role admin
        role = 'admin' if instance.is_superuser else 'student'
        UserProfile.objects.create(user=instance, role=role)



# =============================================================================
# Category — hasil tambahan untuk fitur search & filter (Final Project)
# =============================================================================

class Category(models.Model):
    name = models.CharField("nama kategori", max_length=100, unique=True)
    description = models.TextField("deskripsi", default='-', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategori"


# =============================================================================
# Course
# =============================================================================

class Course(models.Model):
    name = models.CharField("nama matkul", max_length=100)
    description = models.TextField("deskripsi", default='-')
    price = models.IntegerField("harga", default=10000)
    image = models.ImageField("gambar", null=True, blank=True)
    teacher = models.ForeignKey(
        User,
        verbose_name="pengajar",
        on_delete=models.RESTRICT
    )
    # tambahan: category untuk fitur filter (Final Project)
    category = models.ForeignKey(
        Category,
        verbose_name="kategori",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mata Kuliah"
        verbose_name_plural = "Mata Kuliah"


ROLE_OPTIONS = [
    ('std', "Siswa"),
    ('ast', "Asisten"),
]


class CourseMember(models.Model):
    course_id = models.ForeignKey(
        Course,
        verbose_name="matkul",
        on_delete=models.RESTRICT
    )
    user_id = models.ForeignKey(
        User,
        verbose_name="siswa",
        on_delete=models.RESTRICT
    )
    roles = models.CharField(
        "peran",
        max_length=3,
        choices=ROLE_OPTIONS,
        default='std'
    )

    def __str__(self):
        return f"{self.user_id} - {self.course_id} ({self.roles})"

    class Meta:
        verbose_name = "Anggota Kelas"
        verbose_name_plural = "Anggota Kelas"


class CourseContent(models.Model):
    name = models.CharField("judul konten", max_length=200)
    description = models.TextField("deskripsi", default='-')
    video_url = models.CharField(
        'URL Video',
        max_length=200,
        null=True,
        blank=True
    )
    file_attachment = models.FileField("File", null=True, blank=True)
    course_id = models.ForeignKey(
        Course,
        verbose_name="matkul",
        on_delete=models.RESTRICT
    )
    parent_id = models.ForeignKey(
        "self",
        verbose_name="induk",
        on_delete=models.RESTRICT,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Konten Kelas"
        verbose_name_plural = "Konten Kelas"


class Comment(models.Model):
    content_id = models.ForeignKey(
        CourseContent,
        verbose_name="konten",
        on_delete=models.CASCADE
    )
    user_id = models.ForeignKey(
        User,
        verbose_name="penulis",
        on_delete=models.CASCADE
    )
    comment = models.TextField('komentar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Komentar oleh {self.user_id} pada {self.content_id}"

    class Meta:
        verbose_name = "Komentar"
        verbose_name_plural = "Komentar"


# =============================================================================
# Progress — hasil tambahan untuk tracking belajar student (Final Project)
# =============================================================================

PROGRESS_STATUS = [
    ('not_started', 'Belum Dimulai'),
    ('in_progress', 'Sedang Belajar'),
    ('completed', 'Selesai'),
]


class Progress(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="student",
        on_delete=models.CASCADE,
        related_name="progress_list"
    )
    course = models.ForeignKey(
        Course,
        verbose_name="matkul",
        on_delete=models.CASCADE,
        related_name="progress_list"
    )
    content = models.ForeignKey(
        CourseContent,
        verbose_name="konten",
        on_delete=models.CASCADE,
        related_name="progress_list"
    )
    status = models.CharField(
        "status",
        max_length=15,
        choices=PROGRESS_STATUS,
        default='not_started'
    )
    completed_at = models.DateTimeField("selesai pada", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Progress Belajar"
        verbose_name_plural = "Progress Belajar"
        # satu user hanya punya satu progress per content
        unique_together = [('user', 'content')]

    def __str__(self):
        return f"{self.user.username} - {self.content.name} ({self.status})"


# =============================================================================
# Review — rating & review course oleh student (Final Project)
# =============================================================================

RATING_CHOICES = [
    (1, '⭐'),
    (2, '⭐⭐'),
    (3, '⭐⭐⭐'),
    (4, '⭐⭐⭐⭐'),
    (5, '⭐⭐⭐⭐⭐'),
]


class Review(models.Model):
    """
    Review dan rating dari student untuk course yang sudah diikuti.
    Satu student hanya bisa memberikan satu review per course.
    """
    user = models.ForeignKey(
        User,
        verbose_name="reviewer",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    course = models.ForeignKey(
        Course,
        verbose_name="course",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.IntegerField(
        "rating",
        choices=RATING_CHOICES,
        help_text="Rating 1-5"
    )
    comment = models.TextField("komentar review", blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Review"
        unique_together = [('user', 'course')]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.course.name} ({self.rating}⭐)"

