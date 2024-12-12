"""Tests for the student_view_requests view with decorators @login_required and @is_student."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest

class StudentViewRequestsTest(TestCase):

    fixtures = ['tutorials/tests/fixtures/default_user.json',
                'tutorials/tests/fixtures/lesson_requests.json']

    def setUp(self):
        self.student_user = get_user_model().objects.get(username='@charlie')
        self.tutor_user = get_user_model().objects.get(username='@janedoe')
        self.admin_user = get_user_model().objects.get(username='@johndoe')

        # URL for student view requests
        self.url = reverse('student_view_requests')

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/log_in/?next=/lesson_requests/view/')

    def test_is_student_access_only(self):
        # Test tutor access
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        # Test admin access
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_student_can_view_requests(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests/student_view_requests.html')

        requests = LessonRequest.objects.filter(student_id=self.student_user)
        for request in requests:
            self.assertContains(response, request.language)
            self.assertContains(response, request.status)

    def test_no_requests_displayed_for_other_users(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
