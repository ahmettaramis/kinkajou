"""
Tests for URL configuration in the code_tutors project.
"""

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from tutorials import views


class TestURLPatterns(SimpleTestCase):
    def test_admin_url(self):
        url = reverse('admin:index')  # Admin URLs are predefined
        self.assertEqual(resolve(url).func.__module__, 'django.contrib.admin.sites')

    def test_home_url(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, views.home)

    def test_dashboard_url(self):
        url = reverse('dashboard')
        self.assertEqual(resolve(url).func, views.dashboard)

    def test_log_in_url(self):
        url = reverse('log_in')
        self.assertEqual(resolve(url).func.view_class, views.LogInView)

    def test_log_out_url(self):
        url = reverse('log_out')
        self.assertEqual(resolve(url).func, views.log_out)

    def test_password_url(self):
        url = reverse('password')
        self.assertEqual(resolve(url).func.view_class, views.PasswordView)

    def test_profile_url(self):
        url = reverse('profile')
        self.assertEqual(resolve(url).func.view_class, views.ProfileUpdateView)

    def test_sign_up_url(self):
        url = reverse('sign_up')
        self.assertEqual(resolve(url).func.view_class, views.SignUpView)

    def test_tutor_list_view_url(self):
        url = reverse('tutor_list_view')
        self.assertEqual(resolve(url).func.view_class, views.TutorListView)

    def test_update_schedule_url(self):
        url = reverse('update_schedule')
        self.assertEqual(resolve(url).func.view_class, views.TutorAvailabilityUpdateView)

    def test_create_lesson_request_url(self):
        url = reverse('create_lesson_request')
        self.assertEqual(resolve(url).func, views.create_lesson_request)

    def test_student_view_requests_url(self):
        url = reverse('student_view_requests')
        self.assertEqual(resolve(url).func, views.student_view_requests)

    def test_student_view_invoices_url(self):
        url = reverse('student_view_invoices')
        self.assertEqual(resolve(url).func, views.student_view_invoices)

    def test_admin_view_requests_url(self):
        url = reverse('admin_view_requests')
        self.assertEqual(resolve(url).func, views.admin_view_requests)

    def test_update_request_status_url(self):
        url = reverse('update_request_status', kwargs={'pk': 1})
        self.assertEqual(resolve(url).func, views.update_request_status)

    def test_cancel_lesson_url(self):
        url = reverse('cancel_lesson', kwargs={'lesson_id': 1})
        self.assertEqual(resolve(url).func, views.cancel_lesson)

    def test_toggle_invoice_paid_url(self):
        url = reverse('toggle_invoice_paid', kwargs={'invoice_id': 1})
        self.assertEqual(resolve(url).func, views.toggle_invoice_paid)

    def test_generate_invoice_url(self):
        url = reverse('generate_invoice', kwargs={'lesson_request_id': 1})
        self.assertEqual(resolve(url).func, views.generate_invoice)