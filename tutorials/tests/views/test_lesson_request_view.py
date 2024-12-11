from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import LessonRequest, User, AllocatedLesson
from django.utils.timezone import now, timedelta

class LessonRequestViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student1',
            password='password',
            role='student',
            email='student1@example.com'
        )
        self.tutor = User.objects.create_user(
            username='tutor1',
            password='password',
            role='tutor',
            email='tutor1@example.com'
        )
        self.admin = User.objects.create_user(
            username='admin1',
            password='password',
            role='admin',
            email='admin1@example.com'
        )

    def test_student_view_requests(self):
        self.client.login(username='student1', password='password')
        response = self.client.get(reverse('student_view_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests/student_view_requests.html')

    def test_admin_view_requests(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('admin_view_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests/admin_view_requests.html')

    def test_update_request_status(self):
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language="Python",
            term="Sept-Christmas",
            day_of_the_week="Monday",
            frequency="Weekly",
            duration=60,
            status="unallocated",
        )
        self.client.login(username="admin1", password="password")
        response = self.client.post(
            reverse("update_request_status", args=[lesson_request.id]),
            {
                "status": "allocated",
                "lesson_requests_as_tutor": self.tutor.id,
            },
        )
        lesson_request.refresh_from_db()
        self.assertEqual(lesson_request.status, "allocated")
        self.assertEqual(lesson_request.tutor_id, self.tutor)

    def test_student_view_requests(self):
        self.client.login(username='student1', password='password')
        response = self.client.get(reverse('student_view_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_requests/student_view_requests.html')

    def test_tutor_access_student_page(self):
        self.client.login(username='tutor1', password='password')
        response = self.client.get(reverse('student_view_requests'))
        self.assertEqual(response.status_code, 403)  # Tutor should also receive a 403 Forbidden response

    def test_admin_access_student_page(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('student_view_requests'))
        self.assertEqual(response.status_code, 403)  # Admin should not access student page

    def test_student_create_lesson_request(self):
        self.client.login(username='student1', password='password')
        data = {
            'language': 'Python',
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'Learn Python basics.',
            'tutor_id': self.tutor.id,
        }
        response = self.client.post(reverse('create_lesson_request'), data)
        self.assertEqual(response.status_code, 302)  # Should redirect after creation
        self.assertTrue(LessonRequest.objects.filter(student_id=self.student).exists())

    def test_admin_update_request_status_without_tutor(self):
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language="Python",
            term="Sept-Christmas",
            day_of_the_week="Monday",
            frequency="Weekly",
            duration=60,
            description="Learn Python basics.",
        )
        self.client.login(username='admin1', password='password')
        response = self.client.post(reverse('update_request_status', args=[lesson_request.id]), {
            'status': 'allocated',
        })
        self.assertEqual(response.status_code, 200)  # Should show error and not redirect
        lesson_request.refresh_from_db()
        self.assertEqual(lesson_request.status, 'Unallocated')
