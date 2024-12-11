from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now, timedelta
from tutorials.models import User, Tutor, LessonRequest, AllocatedLesson
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class TutorDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create a tutor user
        self.tutor_user = UserModel.objects.create_user(
            username='@tutorexample',
            first_name='John',
            last_name='Doe',
            email='tutor@example.com',
            password='testpass123',
            role='tutor'
        )
        Tutor.objects.create(user=self.tutor_user, subjects='Python')

        # Create a student user
        self.student_user = UserModel.objects.create_user(
            username='@studentexample',
            first_name='Jane',
            last_name='Smith',
            email='student@example.com',
            password='testpass123',
            role='student'
        )

        # Common date for allocated lessons
        self.future_date = (now() + timedelta(days=10)).date()
        self.lesson_time = (now() + timedelta(hours=1)).time()

        # Create a lesson request that links student and tutor
        self.lesson_request = LessonRequest.objects.create(
            student_id=self.student_user,
            tutor_id=self.tutor_user,
            language='Python',
            term='Sept-Christmas',
            day_of_the_week='Wednesday',
            frequency='Weekly',
            duration=60,
            status='allocated'
        )

        # Create allocated lessons for the tutor
        self.allocated_lesson = AllocatedLesson.objects.create(
            lesson_request=self.lesson_request,
            occurrence=1,
            date=self.future_date,
            time=self.lesson_time,
            language='Python',
            student_id=self.student_user,
            tutor_id=self.tutor_user
        )

    def test_tutor_dashboard_valid_data(self):
        """
        Test that a tutor with allocated lessons sees them on the dashboard.
        """
        self.client.login(username='@tutorexample', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tutor Dashboard')
        self.assertContains(response, self.allocated_lesson.language)
        self.assertContains(response, self.allocated_lesson.date.strftime('%Y-%m-%d'))
        self.assertContains(response, self.allocated_lesson.time.strftime('%H:%M'))

    def test_tutor_dashboard_no_lessons(self):
        """
        Test a tutor dashboard when no allocated lessons are present.
        """
        # Create a new tutor with no lessons
        new_tutor = UserModel.objects.create_user(
            username='@lonelytutor',
            first_name='Lonely',
            last_name='Tutor',
            email='lonely@example.com',
            password='testpass123',
            role='tutor'
        )
        Tutor.objects.create(user=new_tutor, subjects='Java')

        self.client.login(username='@lonelytutor', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tutor Dashboard')
        self.assertContains(response, 'You have no allocated lessons at the moment.')

    def test_tutor_dashboard_invalid_role(self):
        """
        Test that a user who is not a tutor sees the correct dashboard and not tutor features.
        """
        self.client.login(username='@studentexample', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        # Student should not see 'Tutor Dashboard'
        self.assertNotContains(response, 'Tutor Dashboard')
        self.assertContains(response, 'Student Dashboard')

    def test_tutor_dashboard_extreme_future_date(self):
        """
        Test a tutor dashboard with an extremely far future allocated lesson.
        """
        # Create an extremely far future lesson date
        far_future_date = (now() + timedelta(days=365 * 5)).date()  # 5 years in the future
        far_future_lesson = AllocatedLesson.objects.create(
            lesson_request=self.lesson_request,
            occurrence=2,
            date=far_future_date,
            time=self.lesson_time,
            language='Python',
            student_id=self.student_user,
            tutor_id=self.tutor_user
        )

        self.client.login(username='@tutorexample', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        # The far future lesson should be displayed as well
        self.assertContains(response, far_future_lesson.date.strftime('%Y-%m-%d'))

    def test_tutor_dashboard_cancellation_form(self):
        """
        Test that the tutor dashboard shows a cancellation form for allocated lessons.
        """
        self.client.login(username='@tutorexample', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        # Confirm that there's a cancel button for the allocated lesson
        cancel_url = reverse('cancel_lesson', args=[self.allocated_lesson.id])
        self.assertContains(response, f'action="{cancel_url}"')
        self.assertContains(response, 'Cancel')
