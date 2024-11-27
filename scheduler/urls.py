#urls.py here is to make views in this app accesible

from django.urls import path
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_lesson, name='create-lesson'),
]