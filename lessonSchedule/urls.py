from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_lesson, name='create_lesson'),
]
