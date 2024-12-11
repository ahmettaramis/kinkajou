from django.test import TestCase
from django.utils.timezone import now, timedelta
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest, AllocatedLesson

User = get_user_model()

class AllocatedLessonModelTest(TestCase):

    def setUp(self):
        # Create a test student and tutor
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

        self.lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            tutor_id=self.tutor,
            language='Python',
            term='Sept-Dec',
            day_of_the_week='Monday',
            frequency='weekly',
            duration=60,
            description='Test description',
            status='Pending'
        )

    def test_create_allocated_lesson(self):
        allocated_lesson = AllocatedLesson(
            lesson_request=self.lesson_request,
            occurrence=1,
            date=now().date() + timedelta(days=7),
            time=now().time(),
            language='Python',
            student_id=self.student,
            tutor_id=self.tutor
        )
        allocated_lesson.clean()
        allocated_lesson.save()

        self.assertEqual(AllocatedLesson.objects.count(), 1)
        self.assertEqual(allocated_lesson.language, 'Python')
        self.assertEqual(allocated_lesson.occurrence, 1)

    def test_unique_together_constraint(self):
        AllocatedLesson.objects.create(
            lesson_request=self.lesson_request,
            occurrence=1,
            date=now().date() + timedelta(days=7),
            time=now().time(),
            language='Python',
            student_id=self.student,
            tutor_id=self.tutor
        )

        with self.assertRaises(ValidationError):
            duplicate_lesson = AllocatedLesson(
                lesson_request=self.lesson_request,
                occurrence=1,
                date=now().date() + timedelta(days=14),
                time=now().time(),
                language='Python',
                student_id=self.student,
                tutor_id=self.tutor
            )
            duplicate_lesson.full_clean()

    def test_clean_method_future_date_validation(self):
        past_date = now().date() - timedelta(days=1)
        allocated_lesson = AllocatedLesson(
            lesson_request=self.lesson_request,
            occurrence=1,
            date=past_date,
            time=now().time(),
            language='Python',
            student_id=self.student,
            tutor_id=self.tutor
        )

        with self.assertRaises(ValidationError):
            allocated_lesson.clean()

    def test_string_representation(self):
        allocated_lesson = AllocatedLesson.objects.create(
            lesson_request=self.lesson_request,
            occurrence=1,
            date=now().date() + timedelta(days=7),
            time=now().time(),
            language='Python',
            student_id=self.student,
            tutor_id=self.tutor
        )
        expected_string = f"Lesson Request {self.lesson_request.id} - Occurrence 1 on {allocated_lesson.date}"
        self.assertEqual(str(allocated_lesson), expected_string)
