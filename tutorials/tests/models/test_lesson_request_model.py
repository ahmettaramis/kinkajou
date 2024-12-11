from django.test import TestCase
from tutorials.models import LessonRequest, User, AllocatedLesson
from django.utils.timezone import now, timedelta

class LessonRequestModelTest(TestCase):
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

    def test_create_lesson_request(self):
        lesson_request = LessonRequest.objects.create(
            student=self.student,
            title="Physics Tutoring",
            description="Focus on mechanics.",
            lesson_date=now() + timedelta(days=3),
            preferred_tutor=self.tutor,
            no_of_weeks=3,
        )
        self.assertEqual(lesson_request.title, "Physics Tutoring")

    def test_allocate_lessons(self):
        lesson_request = LessonRequest.objects.create(
            student=self.student,
            title="Math Tutoring",
            description="Linear algebra lessons.",
            lesson_date=now() + timedelta(days=1),
            preferred_tutor=self.tutor,
            no_of_weeks=2,
            status='allocated',
        )
        allocated_lessons = AllocatedLesson.objects.filter(lesson_request=lesson_request)
        self.assertEqual(allocated_lessons.count(), 2)

    def test_unallocate_lessons(self):
        lesson_request = LessonRequest.objects.create(
            student=self.student,
            title="Math Tutoring",
            description="Linear algebra lessons.",
            lesson_date=now() + timedelta(days=1),
            preferred_tutor=self.tutor,
            no_of_weeks=2,
            status='allocated',
        )
        lesson_request.status = 'unallocated'
        lesson_request.save()
        allocated_lessons = AllocatedLesson.objects.filter(lesson_request=lesson_request)
        self.assertEqual(allocated_lessons.count(), 0)
