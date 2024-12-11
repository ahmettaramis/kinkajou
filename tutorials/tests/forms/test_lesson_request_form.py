from django.test import TestCase
from tutorials.forms import LessonRequestForm
from tutorials.models import User
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
            'title': 'Math Tutoring',
            'description': 'I need help with calculus.',
            'lesson_date': now() + timedelta(days=1),
            'preferred_tutor': self.tutor.id,
            'no_of_weeks': 4,
        }
        form = LessonRequestForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_date_in_past(self):
        data = {
            'title': 'Math Tutoring',
            'description': 'I need help with calculus.',
            'lesson_date': now() - timedelta(days=1),
            'preferred_tutor': self.tutor.id,
            'no_of_weeks': 4,
        }
        form = LessonRequestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Lesson date cannot be in the past.", form.errors['lesson_date'])

    def test_invalid_no_of_weeks(self):
        data = {
            'title': 'Math Lesson',
            'description': 'Learn advanced math.',
            'lesson_date': (now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'no_of_weeks': 53,  # Invalid value
            'preferred_tutor': self.tutor.id,
        }
        form = LessonRequestForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('no_of_weeks', form.errors) 
        self.assertIn(
            "Number of weeks must be between 1 and 52.",
            form.errors['no_of_weeks']
        )
