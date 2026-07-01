"""
Migration: Tambah model UserProfile untuk role system.

Setiap user punya satu profile (OneToOne) dengan field:
- role: admin / instructor / student
- bio: teks opsional

Signal post_save di models.py akan auto-create profile saat user baru dibuat.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0003_add_category_and_progress'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(
                    choices=[('admin', 'Admin'), ('instructor', 'Instructor'), ('student', 'Student')],
                    default='student',
                    max_length=10,
                    verbose_name='peran',
                )),
                ('bio', models.TextField(blank=True, default='', verbose_name='bio')),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='profile',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Profil User',
                'verbose_name_plural': 'Profil User',
            },
        ),
    ]
