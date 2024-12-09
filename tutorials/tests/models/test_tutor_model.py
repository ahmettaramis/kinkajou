from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, Tutor

class TutorModelTestCase(TestCase):
    """Unit tests for the Tutor model."""

    def setUp(self):
        self.user = User.objects.create_user(username="tutor_user", email="tutor@example.com", password="password")
        self.tutor = Tutor.objects.create(user=self.user, subjects="algorithms")

    def test_valid_tutor(self):
        self._assert_tutor_is_valid()

    def test_tutor_subject_cannot_be_invalid(self):
        self.tutor.subjects = "invalid_subject"
        self._assert_tutor_is_invalid()

    def test_tutor_subject_can_be_null(self):
        self.tutor.subjects = None
        self._assert_tutor_is_valid()

    def test_tutor_subject_can_be_blank(self):
        self.tutor.subjects = ""
        self._assert_tutor_is_valid()

    def _assert_tutor_is_valid(self):
        try:
            self.tutor.full_clean()
        except ValidationError:
            self.fail("Tutor should be valid")

    def _assert_tutor_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()
