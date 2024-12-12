"""Tests for the update_request_status view with decorators @login_required and @is_admin."""

from datetime import datetime, time, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import LessonRequest, AllocatedLesson

class UpdateRequestStatusTest(TestCase):

    fixtures = ['tutorials/tests/fixtures/default_user.json',
                'tutorials/tests/fixtures/lesson_requests.json',
                'tutorials/tests/fixtures/allocated_lessons.json']

    def setUp(self):
        self.admin_user = get_user_model().objects.get(username='@johndoe')
        self.student_user = get_user_model().objects.get(username='@charlie')
        self.tutor_user = get_user_model().objects.get(username='@janedoe')

        # Fetch a lesson request for testing
        self.lesson_request = LessonRequest.objects.first()
        self.url = reverse('update_request_status', kwargs={'pk': self.lesson_request.pk})
        self.valid_post_data = {
            'status': 'allocated',
            'lesson_requests_as_tutor': self.tutor_user.id,
            'start_time': '10:00'
        }

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/log_in/?next={self.url}')  # Adjust based on your login URL

    def test_is_admin_access_only(self):
        # Test student access
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        # Test tutor access
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_update_request_status_view(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests/update_request_status.html')

    def test_allocate_lesson_request(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url, self.valid_post_data, follow=True)
        self.assertRedirects(response, reverse('admin_view_requests'))  # Adjust the redirect URL if needed

        # Check status update
        lesson_request = LessonRequest.objects.get(pk=self.lesson_request.pk)
        self.assertEqual(lesson_request.status, 'allocated')
        self.assertEqual(lesson_request.tutor_id, self.tutor_user)

        # Check allocated lessons
        allocated_lessons = AllocatedLesson.objects.filter(lesson_request=lesson_request)
        self.assertTrue(allocated_lessons.exists())

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Lesson request status updated to 'allocated'." in str(m) for m in messages))

    def test_allocation_missing_tutor(self):
        self.valid_post_data.pop('lesson_requests_as_tutor')
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url, self.valid_post_data)
        self.assertEqual(response.status_code, 200)

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("You must assign a tutor before allocating the lesson." in str(m) for m in messages))

    def test_allocation_missing_start_time(self):
        self.valid_post_data.pop('start_time')
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url, self.valid_post_data)
        self.assertEqual(response.status_code, 200)

        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("You must provide a start time before allocating the lesson." in str(m) for m in messages))

    def test_unallocate_allocated_lesson_request(self):
        # Use a lesson_request with pk=2 for the test
        self.lesson_request = LessonRequest.objects.get(pk=2)

        # Update the lesson_request status to 'allocated'
        self.lesson_request.status = 'allocated'
        self.lesson_request.tutor_id = self.tutor_user
        self.lesson_request.save()

        # Add a dummy allocated lesson for this lesson_request
        AllocatedLesson.objects.create(
            lesson_request=self.lesson_request,
            occurrence=1,
            date=datetime.now().date(),
            time=time(10, 0),
            language=self.lesson_request.language,
            student_id=self.lesson_request.student_id,
            tutor_id=self.lesson_request.tutor_id,
        )

        # Log in as admin
        self.client.login(username='@johndoe', password='Password123')

        # Send POST request to update status to 'unallocated'
        response = self.client.post(
            reverse('update_request_status', args=[self.lesson_request.pk]),
            {'status': 'unallocated'},
            follow=True
        )

        # Verify redirect
        self.assertRedirects(response, reverse('admin_view_requests'))

        # Refresh lesson_request from database
        lesson_request = LessonRequest.objects.get(pk=self.lesson_request.pk)

        # Verify status update
        self.assertEqual(lesson_request.status, 'unallocated')

        # Verify allocated lessons are deleted
        allocated_lessons = AllocatedLesson.objects.filter(lesson_request=lesson_request)
        self.assertFalse(allocated_lessons.exists())

        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Allocated lessons have been deleted." in str(m) for m in messages))