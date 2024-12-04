"""Unit tests for the LessonRequest views."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest
from django.utils.timezone import now

User = get_user_model()

class LessonRequestViewTests(TestCase):
    """Unit tests for LessonRequest views."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.client = Client()

        self.student = User.objects.get(username='@peterpickles')
        self.admin = User.objects.get(username='@janedoe')

        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            title="Learn Django",
            description="Request for Django lessons.",
            status="unallocated",
            created_at=now(),
            lesson_date=None,
            preferred_tutor=None,
        )

        self.create_request_url = reverse('create_lesson_request')
        self.student_view_requests_url = reverse('student_view_requests')
        self.admin_view_requests_url = reverse('admin_view_requests')
        self.update_request_status_url = reverse('update_request_status', args=[self.lesson_request.pk])

    def test_create_lesson_request_GET(self):
        self.client.login(username='@peterpickles', password='Password123')
        response = self.client.get(self.create_request_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests/create_request.html')

    def test_create_lesson_request_POST_valid(self):
        self.client.login(username='@peterpickles', password='Password123')
        data = {
            'title': 'Learn Python',
            'description': 'Request for Python lessons.',
            'status': 'unallocated',
        }
        response = self.client.post(self.create_request_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(LessonRequest.objects.count(), 2)

    def test_student_view_requests(self):
        self.client.login(username='@peterpickles', password='Password123')
        response = self.client.get(self.student_view_requests_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests/student_view_requests.html')
        self.assertEqual(len(response.context['requests']), 1)
        self.assertIn(self.lesson_request, response.context['requests'])

    def test_admin_view_requests_no_filter(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.admin_view_requests_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests/admin_view_requests.html')
        self.assertIn(self.lesson_request, response.context['requests'])

    def test_admin_view_requests_with_filter(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.admin_view_requests_url, {'status': 'unallocated'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['requests']), 1)
        self.assertIn(self.lesson_request, response.context['requests'])

    def test_update_request_status_GET(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.update_request_status_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests/update_request_status.html')
        self.assertEqual(response.context['lesson_request'], self.lesson_request)

    def test_update_request_status_POST(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {'status': 'allocated'}
        response = self.client.post(self.update_request_status_url, data)
        self.assertEqual(response.status_code, 302)
        self.lesson_request.refresh_from_db()
        self.assertEqual(self.lesson_request.status, 'allocated')

    def test_unauthorized_access(self):
        response = self.client.get(self.create_request_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
