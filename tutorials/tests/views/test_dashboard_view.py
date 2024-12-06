"""Unit tests for the dashboard.html template."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

User = get_user_model()

class DashboardTemplateTestCase(TestCase):
    """Unit tests for the dashboard.html template."""

    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='@adminuser',
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            role='admin',
            password='Password123'
        )
        self.tutor_user = User.objects.create_user(
            username='@tutoruser',
            first_name='Tutor',
            last_name='User',
            email='tutor@example.com',
            role='tutor',
            password='Password123'
        )
        self.student_user = User.objects.create_user(
            username='@studentuser',
            first_name='Student',
            last_name='User',
            email='student@example.com',
            role='student',
            password='Password123'
        )

    def test_admin_dashboard_renders_correctly(self):
        self.client.login(username='@adminuser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Dashboard")
        self.assertNotContains(response, "Tutor Dashboard")
        self.assertNotContains(response, "Student Dashboard")

    def test_tutor_dashboard_renders_correctly(self):
        self.client.login(username='@tutoruser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Admin Dashboard")
        self.assertContains(response, "Tutor Dashboard")
        self.assertNotContains(response, "Student Dashboard")

    def test_student_dashboard_renders_correctly(self):
        self.client.login(username='@studentuser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Admin Dashboard")
        self.assertNotContains(response, "Tutor Dashboard")
        self.assertContains(response, "Student Dashboard")
