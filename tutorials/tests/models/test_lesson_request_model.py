from django.test import TestCase
from tutorials.models import LessonRequest, AllocatedLesson, User
from django.utils.timezone import now

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
            student_id=self.student,
            language='Python',
            term='Sept-Christmas',
            day_of_the_week='Monday',
            frequency='Weekly',
            duration=60,
            description='Learn Python basics.',
            tutor_id=self.tutor,
        )
        self.assertEqual(lesson_request.language, 'Python')
        self.assertEqual(lesson_request.tutor_id, self.tutor)

    def test_allocate_lessons(self):
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language='Python',
            term='Sept-Christmas',
            day_of_the_week='Monday',
            frequency='Weekly',
            duration=60,
            description='Learn Python basics.',
            tutor_id=self.tutor,
            status='allocated',
        )
        allocated_lessons = AllocatedLesson.objects.filter(lesson_request=lesson_request)
        self.assertTrue(allocated_lessons.exists())

    def test_unallocate_lessons(self):
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language='Python',
            term='Sept-Christmas',
            day_of_the_week='Monday',
            frequency='Weekly',
            duration=60,
            description='Learn Python basics.',
            tutor_id=self.tutor,
            status='allocated',
        )
        AllocatedLesson.objects.filter(lesson_request=lesson_request).delete()
        allocated_lessons = AllocatedLesson.objects.filter(lesson_request=lesson_request)
        self.assertFalse(allocated_lessons.exists())
