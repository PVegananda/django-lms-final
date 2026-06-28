"""
Migrasi tambahan untuk Final Project:
- Tambah model Category (untuk filter dan kategorisasi course)
- Tambah field category ke model Course
- Tambah model Progress (tracking belajar student per konten)
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_coursecontent_created_at_coursecontent_updated_at'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Buat tabel Category
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='nama kategori')),
                ('description', models.TextField(blank=True, default='-', verbose_name='deskripsi')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Kategori',
                'verbose_name_plural': 'Kategori',
            },
        ),
        # 2. Tambah kolom category ke Course (nullable, agar data lama tetap aman)
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='courses',
                to='courses.category',
                verbose_name='kategori',
            ),
        ),
        # 3. Buat tabel Progress
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('not_started', 'Belum Dimulai'),
                        ('in_progress', 'Sedang Belajar'),
                        ('completed', 'Selesai'),
                    ],
                    default='not_started',
                    max_length=15,
                    verbose_name='status',
                )),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='selesai pada')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='progress_list',
                    to='courses.coursecontent',
                    verbose_name='konten',
                )),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='progress_list',
                    to='courses.course',
                    verbose_name='matkul',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='progress_list',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='student',
                )),
            ],
            options={
                'verbose_name': 'Progress Belajar',
                'verbose_name_plural': 'Progress Belajar',
                'unique_together': {('user', 'content')},
            },
        ),
    ]
