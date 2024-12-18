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
            student_id=self.student,
            language="Python",
            term="Sept-Christmas",
            day_of_the_week="Monday",
            frequency="Weekly",
            duration=60,
            description="Python tutoring needed.",
            tutor_id=self.tutor,
            status="Pending"
        )
        self.assertEqual(lesson_request.language, "Python")
        self.assertEqual(lesson_request.term, "Sept-Christmas")
        self.assertEqual(lesson_request.status, "Pending")

    def test_allocate_lessons(self):
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language="Python",
            term="Jan-Easter",
            day_of_the_week="Tuesday",
            frequency="Weekly",
            duration=60,
            description="Learn Python basics.",
            tutor_id=self.tutor,
            status="allocated",
        )
        AllocatedLesson.objects.create(
            lesson_request=lesson_request,
            occurrence=1,
            date=now().date() + timedelta(days=7),
            time=now().time(),
            language="Python",
            student_id=self.student,
            tutor_id=self.tutor,
        )
        allocated_lessons = AllocatedLesson.objects.filter(lesson_request=lesson_request)
        self.assertEqual(allocated_lessons.count(), 1)

    def test_unallocate_lessons(self):
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language="Python",
            term="March-June",
            day_of_the_week="Friday",
            frequency="Weekly",
            duration=60,
            tutor_id=self.tutor,
            status="allocated",
        )
        AllocatedLesson.objects.create(
            lesson_request=lesson_request,
            occurrence=1,
            date=now().date() + timedelta(days=7),
            time=now().time(),
            language="Python",
            student_id=self.student,
            tutor_id=self.tutor,
        )
        lesson_request.status = "unallocated"
        lesson_request.save()
        AllocatedLesson.objects.filter(lesson_request=lesson_request).delete()
        allocated_lessons = AllocatedLesson.objects.filter(lesson_request=lesson_request)
        self.assertEqual(allocated_lessons.count(), 0)

    def test_create_lesson_request(self):
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language="Python",
            term="Sept-Christmas",
            day_of_the_week="Monday",
            frequency="Weekly",
            duration=60,
            description="Learn Python basics."
        )
        self.assertEqual(lesson_request.language, "Python")

    def test_lesson_request_auto_status(self):
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language="Python",
            term="Sept-Christmas",
            day_of_the_week="Monday",
            frequency="Weekly",
            duration=60,
            description="Learn Python basics."
        )
        self.assertEqual(lesson_request.status, "Unallocated")

    def test_tutor_assignment(self):
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language="Python",
            term="Sept-Christmas",
            day_of_the_week="Monday",
            frequency="Weekly",
            duration=60,
            description="Learn Python basics.",
            tutor_id=self.tutor,
        )
        self.assertEqual(lesson_request.tutor_id, self.tutor)

    def test_lesson_request_with_no_description(self):
        """Test lesson request creation without a description."""
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language="Python",
            term="Sept-Christmas",
            day_of_the_week="Monday",
            frequency="Weekly",
            duration=60
        )
        self.assertEqual(lesson_request.description, "")

    def test_allocated_lesson_duplicate_occurrence(self):
        """Ensure duplicate occurrences for the same request are not allowed."""
        lesson_request = LessonRequest.objects.create(
            student_id=self.student,
            language="Python",
            term="Jan-Easter",
            day_of_the_week="Tuesday",
            frequency="Weekly",
            duration=60,
            tutor_id=self.tutor,
        )
        AllocatedLesson.objects.create(
            lesson_request=lesson_request,
            occurrence=1,
            date=now().date() + timedelta(days=7),
            time=now().time(),
            language="Python",
            student_id=self.student,
            tutor_id=self.tutor,
        )
        with self.assertRaises(Exception):  # Should raise an integrity error
            AllocatedLesson.objects.create(
                lesson_request=lesson_request,
                occurrence=1,
                date=now().date() + timedelta(days=14),
                time=now().time(),
                language="Python",
                student_id=self.student,
                tutor_id=self.tutor,
            )
