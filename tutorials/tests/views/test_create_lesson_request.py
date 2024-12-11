from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest

User = get_user_model()


class CreateLessonRequestViewTest(TestCase):
    fixtures = ['tutorials/tests/fixtures/default_user.json',
                'tutorials/tests/fixtures/lesson_requests.json']

    def setUp(self):
        self.student_user = get_user_model().objects.get(username='@charlie')
        self.tutor_user = get_user_model().objects.get(username='@janedoe')
        self.admin_user = get_user_model().objects.get(username='@johndoe')

        # URL for creating a lesson request
        self.url = reverse('create_lesson_request')

        # Log in the student user
        self.client.login(username='@charlie', password='Password123')

    def test_create_lesson_request_valid(self):
        # Prepare valid data for the form
        data = {
            'language': 'Python',
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'Looking for a tutor to help with Python.',
            'tutor_id': self.tutor_user.id  # Selecting a tutor
        }

        # Make the POST request
        response = self.client.post(self.url, data)

        # Check that the lesson request is saved in the database
        self.assertEqual(LessonRequest.objects.count(), 3)  # 2 from fixtures, 1 new
        lesson_request = LessonRequest.objects.last()  # The newly created request
        self.assertEqual(lesson_request.language, 'Python')
        self.assertEqual(lesson_request.term, 'Sept-Christmas')
        self.assertEqual(lesson_request.day_of_the_week, 'Monday')
        self.assertEqual(lesson_request.frequency, 'Weekly')
        self.assertEqual(lesson_request.duration, 60)
        self.assertEqual(lesson_request.description, 'Looking for a tutor to help with Python.')
        self.assertEqual(lesson_request.tutor_id, self.tutor_user)
        self.assertEqual(lesson_request.student_id, self.student_user)
        self.assertRedirects(response, reverse('student_view_requests'))

    def test_create_lesson_request_invalid_missing_language(self):
        data = {
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'Looking for a tutor.',
            'tutor_id': self.tutor_user.id
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('language', form.errors)
        self.assertIn('This field is required.', form.errors['language'])

        # Ensure no new lesson request was created
        self.assertEqual(LessonRequest.objects.count(), 2)

    def test_create_lesson_request_invalid_invalid_tutor(self):
        invalid_user = User.objects.create_user(
            username='invalid_user',
            password='password123',
            role='student'
        )
        data = {
            'language': 'Python',
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'Looking for a tutor to help with Python.',
            'tutor_id': invalid_user.id
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertTrue(form.errors)

        self.assertIn('tutor_id', form.errors)
        self.assertIn('Select a valid choice. That choice is not one of the available choices.', form.errors['tutor_id'])

        self.assertEqual(LessonRequest.objects.count(), 2)

    def test_create_lesson_request_without_tutor(self):
        # Prepare valid data without selecting a tutor
        data = {
            'language': 'Python',
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'Looking for a tutor to help with Python.',
            'tutor_id': ''  # No tutor selected
        }

        # Make the POST request
        response = self.client.post(self.url, data)

        # Check that the lesson request is saved in the database without tutor
        self.assertEqual(LessonRequest.objects.count(), 3)  # 2 from fixtures, 1 new
        lesson_request = LessonRequest.objects.last()
        self.assertEqual(lesson_request.tutor_id, None)
        self.assertRedirects(response, reverse('student_view_requests'))

    def test_create_lesson_request_student_not_logged_in(self):
        # Log out the user to simulate not being logged in
        self.client.logout()

        # Try to access the lesson request creation page
        response = self.client.get(self.url)

        # Ensure the user is redirected to the login page
        self.assertRedirects(response, f'/log_in/?next={self.url}')

    def test_create_lesson_request_invalid_description(self):
        data = {
            'language': 'Python',
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'A' * 1001,
            'tutor_id': self.tutor_user.id
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertTrue(form.errors)

        self.assertIn('description', form.errors)
        self.assertIn('Description cannot exceed 1000 characters.', form.errors['description'])

        self.assertEqual(LessonRequest.objects.count(), 2)

