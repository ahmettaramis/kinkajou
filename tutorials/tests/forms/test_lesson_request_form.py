from django.test import TestCase
from tutorials.forms import LessonRequestForm
from tutorials.models import User, LessonRequest
from django.utils.timezone import now, timedelta

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
            'description': 'Looking for help with Python basics.',
            'tutor_id': self.tutor.id,
        }
        form = LessonRequestForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_no_tutor_role(self):
        invalid_user = User.objects.create_user(
            username='user1',
            password='password',
            role='student',
            email='user1@example.com'
        )
        data = {
            'language': 'Python',
            'term': 'Jan-Easter',
            'day_of_the_week': 'Tuesday',
            'frequency': 'Weekly',
            'duration': 60,
            'tutor_id': invalid_user.id,
        }
        form = LessonRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Select a valid choice. That choice is not one of the available choices.", form.errors['tutor_id'])

    def test_invalid_duration(self):
        data = {
            'language': 'Python',
            'term': 'March-June',
            'day_of_the_week': 'Friday',
            'frequency': 'Weekly',
            'duration': 90,  # Invalid duration
        }
        form = LessonRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Select a valid choice. 90 is not one of the available choices.", form.errors['duration'])

    def test_valid_form(self):
        data = {
            'language': 'Python',
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'Help with Python basics.',
            'tutor_id': self.tutor.id,
        }
        form = LessonRequestForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_language(self):
        data = {
            'language': 'InvalidLang',  # Invalid language
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'Help with Python basics.',
            'tutor_id': self.tutor.id,
        }
        form = LessonRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('language', form.errors)

    def test_missing_tutor_field(self):
        data = {
            'language': 'Python',
            'term': 'Sept-Christmas',
            'day_of_the_week': 'Monday',
            'frequency': 'Weekly',
            'duration': 60,
            'description': 'Help with Python basics.',
            # Missing tutor_id
        }
        form = LessonRequestForm(data=data)
        self.assertTrue(form.is_valid())
