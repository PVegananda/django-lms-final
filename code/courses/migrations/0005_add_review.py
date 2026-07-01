"""
Migration: Tambah model Review untuk rating & review course.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0004_add_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(
                    choices=[(1, '⭐'), (2, '⭐⭐'), (3, '⭐⭐⭐'), (4, '⭐⭐⭐⭐'), (5, '⭐⭐⭐⭐⭐')],
                    help_text='Rating 1-5',
                    verbose_name='rating',
                )),
                ('comment', models.TextField(blank=True, default='', verbose_name='komentar review')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reviews',
                    to='courses.course',
                    verbose_name='course',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reviews',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='reviewer',
                )),
            ],
            options={
                'verbose_name': 'Review',
                'verbose_name_plural': 'Review',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'course')},
            },
        ),
    ]
