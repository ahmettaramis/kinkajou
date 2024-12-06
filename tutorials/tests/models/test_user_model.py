"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User

class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

    # Username Tests
    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_must_start_with_at_symbol(self):
        self.user.username = 'johndoe'
        self._assert_user_is_invalid()

    def test_username_must_contain_at_least_3_alphanumericals_after_at(self):
        self.user.username = '@jo'
        self._assert_user_is_invalid()

    def test_username_can_be_30_characters_long(self):
        self.user.username = '@' + 'x' * 29
        self._assert_user_is_valid()

    def test_username_cannot_be_over_30_characters_long(self):
        self.user.username = '@' + 'x' * 30
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.username = second_user.username
        self._assert_user_is_invalid()

    # First Name Tests
    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    # Last Name Tests
    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()

    # Email Tests
    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        second_user = User.objects.get(username='@janedoe')
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    # Role Tests
    def test_default_role_is_student(self):
        self.assertEqual(self.user.role, 'student')

    def test_role_must_be_valid_choice(self):
        self.user.role = 'invalid_role'
        self._assert_user_is_invalid()

    def test_role_can_be_admin(self):
        self.user.role = 'admin'
        self._assert_user_is_valid()

    def test_role_can_be_tutor(self):
        self.user.role = 'tutor'
        self._assert_user_is_valid()

    # Full Name Test
    def test_full_name_must_be_correct(self):
        full_name = self.user.full_name()
        self.assertEqual(full_name, "John Doe")

    # Gravatar Tests
    def test_default_gravatar(self):
        actual_gravatar_url = self.user.gravatar()
        self.assertIn("https://www.gravatar.com/avatar/", actual_gravatar_url)

    def test_custom_gravatar(self):
        actual_gravatar_url = self.user.gravatar(size=100)
        self.assertIn("size=100", actual_gravatar_url)

    def test_mini_gravatar(self):
        actual_gravatar_url = self.user.mini_gravatar()
        self.assertIn("size=60", actual_gravatar_url)

    # Helper Methods
    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
