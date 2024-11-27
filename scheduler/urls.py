#urls.py here is to make views in this app accesible

from django.urls import path
from . import views

urlpatterns = [
    path('schedule/', views.schedule_lesson, name='schedule-lesson'),
]