"""Unit tests for the LessonRequest model."""

from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, LessonRequest
from django.utils.timezone import now
from datetime import datetime, timedelta

class LessonRequestModelTestCase(TestCase):
    """Unit tests for the LessonRequest model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.admin = User.objects.get(username='@janedoe')  # Admin only
        self.tutor = User.objects.get(username='@petrapickles')  # Tutor only
        self.student = User.objects.get(username='@peterpickles')  # Student only
        self.admin_tutor = User.objects.get(username='@johndoe')  # Admin and Tutor

        self.lesson_request = LessonRequest(
            student=self.student,
            title="Learn Python",
            description="A lesson request for beginner Python programming.",
            status="unallocated",
            created_at=now(),
            lesson_date=None,
            preferred_tutor=None,
        )

    """Unit tests for student in LessonRequest model."""
    def test_student_can_submit_lesson_request(self):
        self._assert_lesson_request_is_valid()

    def test_tutor_cannot_submit_lesson_request(self):
        self.lesson_request.student = self.tutor
        self._assert_lesson_request_is_invalid()

    def test_admin_cannot_submit_lesson_request(self):
        self.lesson_request.student = self.admin
        self._assert_lesson_request_is_invalid()

    def test_admin_and_tutor_cannot_submit_lesson_request(self):
        self.lesson_request.student = self.admin_tutor
        self._assert_lesson_request_is_invalid()

    """Unit tests for title in LessonRequest model."""

    def test_title_cannot_be_none(self):
        self.lesson_request.title = None
        self._assert_lesson_request_is_invalid()

    def test_title_cannot_be_empty(self):
        self.lesson_request.title = ''
        self._assert_lesson_request_is_invalid()

    def test_title_cannot_be_spaces(self):
        self.lesson_request.title = '              '.replace(" ", "")
        self._assert_lesson_request_is_invalid()

    def test_title_can_be_255_characters(self):
        self.lesson_request.title = 'x' * 255
        self._assert_lesson_request_is_valid()

    def test_title_cannot_exceed_255_characters(self):
        self.lesson_request.title = 'x' * 256
        self._assert_lesson_request_is_invalid()

    """Unit tests for status in LessonRequest model."""

    def test_status_cannot_be_none(self):
        self.lesson_request.status = None
        self._assert_lesson_request_is_invalid()

    def test_status_cannot_be_empty(self):
        self.lesson_request.status = ''
        self._assert_lesson_request_is_invalid()

    def test_status_cannot_be_spaces(self):
        self.lesson_request.status = '              '.replace(" ", "")
        self._assert_lesson_request_is_invalid()

    def test_status_can_be_unallocated(self):
        self.lesson_request.status = 'unallocated'
        self._assert_lesson_request_is_valid()

    def test_status_can_be_allocated(self):
        self.lesson_request.status = 'allocated'
        self._assert_lesson_request_is_valid()

    def test_status_cannot_be_invalid_status(self):
        self.lesson_request.status = 'invalid_status'
        self._assert_lesson_request_is_invalid()

    """Unit tests for lesson_date in LessonRequest model."""

    def test_lesson_date_can_be_none(self):
        self.lesson_request.lesson_date = None
        self._assert_lesson_request_is_valid()

    def test_lesson_date_cannot_be_empty(self):
        self.lesson_request.lesson_date = ''
        self._assert_lesson_request_is_invalid()

    def test_lesson_date_can_be_in_the_future(self):
        self.lesson_request.lesson_date = self.lesson_request.created_at + timedelta(days=2)
        self._assert_lesson_request_is_valid()

    def test_lesson_date_cannot_be_in_the_past(self):
        self.lesson_request.lesson_date = self.lesson_request.created_at - timedelta(days=2)
        self._assert_lesson_request_is_invalid()

    """Unit tests for preferred_tutor in LessonRequest model."""

    def test_student_cannot_be_preferred_tutor(self):
        self.lesson_request.preferred_tutor = self.student
        self._assert_lesson_request_is_invalid()

    def test_tutor_can_be_preferred_tutor(self):
        self.lesson_request.preferred_tutor = self.tutor
        self._assert_lesson_request_is_valid()

    def test_admin_cannot_be_preferred_tutor(self):
        self.lesson_request.preferred_tutor = self.admin
        self._assert_lesson_request_is_invalid()

    def test_admin_and_tutor_can_be_preferred_tutor(self):
        self.lesson_request.preferred_tutor = self.admin_tutor
        self._assert_lesson_request_is_valid()


    def _assert_lesson_request_is_valid(self):
        try:
            self.lesson_request.full_clean()
        except ValidationError:
            self.fail("Test lesson request should be valid")

    def _assert_lesson_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.lesson_request.full_clean()
