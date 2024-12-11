from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import LessonRequest, User
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
            student=self.student,
            title="Physics Tutoring",
            description="Mechanics focus.",
            lesson_date=now() + timedelta(days=3),
            status='unallocated',
            no_of_weeks=2,
        )
        self.client.login(username='admin1', password='password')
        response = self.client.post(reverse('update_request_status', args=[lesson_request.id]), {
            'status': 'allocated',
            'preferred_tutor': self.tutor.id,
        })
        lesson_request.refresh_from_db()
        self.assertEqual(lesson_request.status, 'allocated')
        self.assertEqual(lesson_request.preferred_tutor, self.tutor)
