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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    # Tutor views
    path('tutors/', views.TutorListView.as_view(), name='tutor_list_view'),
    path('update_schedule/', views.TutorAvailabilityUpdateView.as_view(), name='update_schedule'),
     # Student views
    path('lesson_requests/create/', views.create_lesson_request, name='create_lesson_request'),
    path('lesson_requests/view/', views.student_view_requests, name='student_view_requests'),
    path('student_view_invoices/', views.student_view_invoices, name='student_view_invoices'),
    # Admin views
    path('lesson_requests/admin/', views.admin_view_requests, name='admin_view_requests'),
    path('lesson_requests/<int:pk>/update-status/', views.update_request_status, name='update_request_status'),
    
    path('toggle-invoice-paid/<int:invoice_id>/', views.toggle_invoice_paid, name='toggle_invoice_paid'),
    path('generate_invoice/<int:lesson_request_id>/', views.generate_invoice, name='generate_invoice'),
] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
