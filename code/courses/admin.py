from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Course, CourseMember, CourseContent, Comment, Category, Progress, UserProfile, Review


# UserProfile inline — tampil di halaman edit User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "Profil"
    verbose_name_plural = "Profil"


# Extend default UserAdmin supaya ada inline profile
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]


# Unregister User bawaan, register ulang dengan inline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'category', 'price', 'created_at')
    list_filter = ('teacher', 'category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)


@admin.register(CourseMember)
class CourseMemberAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'user_id', 'roles')
    list_filter = ('roles',)


@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_id', 'parent_id')
    list_filter = ('course_id',)
    search_fields = ('name', 'description')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content_id', 'user_id', 'comment')
    list_filter = ('content_id',)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'content', 'status', 'completed_at')
    list_filter = ('status', 'course')
    search_fields = ('user__username', 'content__name')
    ordering = ('-updated_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'course')
    search_fields = ('user__username', 'course__name', 'comment')
    ordering = ('-created_at',)
