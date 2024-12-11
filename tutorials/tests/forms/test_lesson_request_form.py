from django.test import TestCase
from tutorials.forms import LessonRequestForm
from tutorials.models import User
from django.utils.timezone import now

class LessonRequestFormTest(TestCase):
    def setUp(self):
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

    def test_valid_form(self):
        data = {
            'language': 'Python',
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'I need help with Python basics.',
            'tutor_id': self.tutor.id,
        }
        form = LessonRequestForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_no_of_weeks(self):
        data = {
            'language': 'Python',
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'I need help with Python basics.',
            'tutor_id': self.tutor.id,
        }
        form = LessonRequestForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_tutor(self):
        data = {
            'language': 'Python',
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'I need help with Python basics.',
            'tutor_id': self.student.id,  # Invalid tutor (student role)
        }
        form = LessonRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Selected user is not a tutor.", form.errors['tutor_id'])
