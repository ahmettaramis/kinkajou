from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, Tutor, Student

class StudentModelTestCase(TestCase):
    """Unit tests for the Student model."""

    def setUp(self):
        # Create a user for the student
        self.student_user = User.objects.create_user(username="student_user", email="student@example.com", password="password")

        # Create a user for the tutor
        self.tutor_user = User.objects.create_user(username="tutor_user", email="tutor@example.com", password="password")
        
        # Create a tutor linked to the tutor user
        self.tutor = Tutor.objects.create(user=self.tutor_user, subjects="python")
        
        # Create a student linked to the student user
        self.student = Student.objects.create(user=self.student_user, tutor=self.tutor)

    def test_valid_student(self):
        """Test that a valid student instance is valid."""
        self._assert_student_is_valid()

    def test_student_can_have_no_tutor(self):
        """Test that a student can exist without a tutor assigned."""
        self.student.tutor = None
        self._assert_student_is_valid()

    def test_student_tutor_must_be_tutor_instance(self):
        """Test that assigning a non-Tutor instance to tutor raises an error."""
        with self.assertRaises(ValueError):
            # Attempt to assign a User instance instead of a Tutor instance
            self.student.tutor = self.student_user

    def test_student_str(self):
        self.assertEqual(str(self.student), f"{self.student_user.username}")

    def _assert_student_is_valid(self):
        """Helper method to check if a student instance is valid."""
        try:
            self.student.full_clean()
        except ValidationError:
            self.fail("Student should be valid")

    def _assert_student_is_invalid(self):
        """Helper method to check if a student instance is invalid."""
        with self.assertRaises(ValidationError):
            self.student.full_clean()
