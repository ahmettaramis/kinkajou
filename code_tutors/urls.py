"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views
from tutorials.views import CustomLoginView, role_based_redirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('role-based-redirect/', role_based_redirect, name='role_based_redirect'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tutor-dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('request-lesson/', views.request_lesson, name='request_lesson'),
    path('schedule-lesson/<int:lesson_id>/', views.schedule_lesson, name='schedule_lesson'),
    path('invoices/', views.view_invoices, name='view_invoices'),
    path('student-schedule/', views.student_schedule, name='student_schedule'),
    path('tutor-schedule/', views.tutor_schedule, name='tutor_schedule'),
    # Admin specific
    path('assign-tutor/<int:lesson_id>/', views.assign_tutor, name='assign_tutor'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)