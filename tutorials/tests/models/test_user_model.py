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
        self.admin = User.objects.get(username='@johndoe')
        self.tutor = User.objects.get(username='@janedoe')
        self.student = User.objects.get(username='@charlie')

    # Helper Methods
    def _assert_user_is_valid(self, user):
        try:
            user.full_clean()
        except ValidationError:
            self.fail(f'Test user {user.username} should be valid')

    def _assert_user_is_invalid(self, user):
        with self.assertRaises(ValidationError):
            user.full_clean()

    # Username Tests
    def test_usernames_cannot_be_blank(self):
        for user in [self.admin, self.tutor, self.student]:
            user.username = ''
            self._assert_user_is_invalid(user)

    def test_usernames_must_start_with_at_symbol(self):
        for user in [self.admin, self.tutor, self.student]:
            user.username = user.username[1:]  # Remove the @ symbol
            self._assert_user_is_invalid(user)

    def test_usernames_must_contain_at_least_3_alphanumericals_after_at(self):
        for user in [self.admin, self.tutor, self.student]:
            user.username = '@ab'
            self._assert_user_is_invalid(user)

    def test_usernames_can_be_30_characters_long(self):
        for user in [self.admin, self.tutor, self.student]:
            user.username = '@' + 'x' * 29
            self._assert_user_is_valid(user)

    def test_usernames_cannot_be_over_30_characters_long(self):
        for user in [self.admin, self.tutor, self.student]:
            user.username = '@' + 'x' * 30
            self._assert_user_is_invalid(user)

    def test_usernames_must_be_unique(self):
        self.admin.username = self.tutor.username
        self._assert_user_is_invalid(self.admin)

    # First Name Tests
    def test_first_names_cannot_be_blank(self):
        for user in [self.admin, self.tutor, self.student]:
            user.first_name = ''
            self._assert_user_is_invalid(user)

    def test_first_names_may_contain_50_characters(self):
        for user in [self.admin, self.tutor, self.student]:
            user.first_name = 'x' * 50
            self._assert_user_is_valid(user)

    def test_first_names_cannot_contain_more_than_50_characters(self):
        for user in [self.admin, self.tutor, self.student]:
            user.first_name = 'x' * 51
            self._assert_user_is_invalid(user)

    # Last Name Tests
    def test_last_names_cannot_be_blank(self):
        for user in [self.admin, self.tutor, self.student]:
            user.last_name = ''
            self._assert_user_is_invalid(user)

    def test_last_names_may_contain_50_characters(self):
        for user in [self.admin, self.tutor, self.student]:
            user.last_name = 'x' * 50
            self._assert_user_is_valid(user)

    def test_last_names_cannot_contain_more_than_50_characters(self):
        for user in [self.admin, self.tutor, self.student]:
            user.last_name = 'x' * 51
            self._assert_user_is_invalid(user)

    # Email Tests
    def test_emails_cannot_be_blank(self):
        for user in [self.admin, self.tutor, self.student]:
            user.email = ''
            self._assert_user_is_invalid(user)

    def test_emails_must_be_unique(self):
        self.admin.email = self.tutor.email
        self._assert_user_is_invalid(self.admin)

    # Role Tests
    def test_default_roles(self):
        self.assertEqual(self.admin.role, 'admin')
        self.assertEqual(self.tutor.role, 'tutor')
        self.assertEqual(self.student.role, 'student')

    def test_roles_must_be_valid_choices(self):
        for user in [self.admin, self.tutor, self.student]:
            user.role = 'invalid_role'
            self._assert_user_is_invalid(user)

    def test_roles_can_be_changed_to_valid_choices(self):
        valid_roles = ['admin', 'tutor', 'student']
        for user in [self.admin, self.tutor, self.student]:
            for role in valid_roles:
                user.role = role
                self._assert_user_is_valid(user)

    # Full Name Test
    def test_full_names_must_be_correct(self):
        self.assertEqual(self.admin.full_name(), "John Doe")
        self.assertEqual(self.tutor.full_name(), "Jane Doe")
        self.assertEqual(self.student.full_name(), "Charlie Johnson")

    # Gravatar Tests
    def test_default_gravatars(self):
        for user in [self.admin, self.tutor, self.student]:
            actual_gravatar_url = user.gravatar()
            self.assertIn("https://www.gravatar.com/avatar/", actual_gravatar_url)

    def test_custom_gravatars(self):
        for user in [self.admin, self.tutor, self.student]:
            actual_gravatar_url = user.gravatar(size=100)
            self.assertIn("size=100", actual_gravatar_url)

    def test_mini_gravatars(self):
        for user in [self.admin, self.tutor, self.student]:
            actual_gravatar_url = user.mini_gravatar()
            self.assertIn("size=60", actual_gravatar_url)
