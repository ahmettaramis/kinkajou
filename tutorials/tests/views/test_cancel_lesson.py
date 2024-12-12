"""Unit tests for the cancel_lesson view."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import AllocatedLesson, LessonRequest

class CancelLessonTestCase(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/allocated_lessons.json',
        'tutorials/tests/fixtures/lesson_requests.json'
    ]

    def setUp(self):
        self.student_user = get_user_model().objects.get(username='@charlie')
        self.tutor_user = get_user_model().objects.get(username='@janedoe')
        self.admin_user = get_user_model().objects.get(username='@johndoe')

        # Use an existing AllocatedLesson from the fixtures
        self.lesson = AllocatedLesson.objects.first()
        self.url = reverse('cancel_lesson', args=[self.lesson.id])

    def test_cancel_lesson_redirects_if_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_student_cannot_cancel_lesson(self):
        self.client.force_login(self.student_user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(AllocatedLesson.objects.filter(id=self.lesson.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "You do not have permission to cancel this lesson.")

    def test_tutor_can_cancel_lesson(self):
        self.client.force_login(self.tutor_user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(AllocatedLesson.objects.filter(id=self.lesson.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Lesson has been cancelled successfully.")

    def test_other_user_cannot_cancel_lesson(self):
        other_user = get_user_model().objects.get(username='@petrapickles')
        self.client.force_login(other_user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(AllocatedLesson.objects.filter(id=self.lesson.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "You do not have permission to cancel this lesson.")

    def test_get_request_does_not_cancel_lesson(self):
        self.client.force_login(self.student_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertTrue(AllocatedLesson.objects.filter(id=self.lesson.id).exists())
