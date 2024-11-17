from django.contrib import admin
from .models import LessonRequest, TutorAvailability, Lesson, Invoice

# Register your models here.

@admin.action(description="Mark selected requests as approved")
def approve_requests(modeladmin, request, queryset):
    queryset.update(status='approved')

@admin.register(LessonRequest)
class LessonRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'topic', 'preferred_time', 'status']
    actions = [approve_requests]