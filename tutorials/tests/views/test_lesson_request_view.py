from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import LessonRequest, User

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
                "start_time": "10:00",
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
        self.assertEqual(response.status_code, 403)

    def test_admin_access_student_page(self):
        self.client.login(username='admin1', password='password')
        response = self.client.get(reverse('student_view_requests'))
        self.assertEqual(response.status_code, 403)

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
        self.assertEqual(response.status_code, 302)
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
        self.assertEqual(response.status_code, 200)
        lesson_request.refresh_from_db()
        self.assertEqual(lesson_request.status, 'Unallocated')

    def test_student_view_unauthenticated(self):
        """Ensure unauthenticated users cannot access student view."""
        response = self.client.get(reverse('student_view_requests'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_admin_view_unauthenticated(self):
        """Ensure unauthenticated users cannot access admin view."""
        response = self.client.get(reverse('admin_view_requests'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_create_request_invalid_data(self):
        """Ensure invalid data does not create a lesson request."""
        self.client.login(username='student1', password='password')
        data = {
            'language': 'InvalidLang',
            'term': 'InvalidTerm',
            'day_of_the_week': 'InvalidDay',
            'frequency': 'InvalidFreq',
            'duration': 90,  # Invalid duration
        }
        response = self.client.post(reverse('create_lesson_request'), data)
        self.assertEqual(response.status_code, 200)  # Should remain on the form page
        self.assertFalse(LessonRequest.objects.filter(student_id=self.student).exists())

    def test_tutor_cannot_access_admin_view(self):
        """Ensure tutors cannot access admin-specific views."""
        self.client.login(username='tutor1', password='password')
        response = self.client.get(reverse('admin_view_requests'))
        self.assertEqual(response.status_code, 403)  # Forbidden
