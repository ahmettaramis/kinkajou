"""Unit tests of the user form."""
from django import forms
from django.test import TestCase
from tutorials.forms import UserForm
from tutorials.models import User

class UserFormTestCase(TestCase):
    """Unit tests of the user form."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',
            'email': 'janedoe@example.org',
            'role': 'student'
        }

    def test_form_has_necessary_fields(self):
        form = UserForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('role', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        role_field = form.fields['role']
        self.assertTrue(isinstance(role_field, forms.ChoiceField))

    def test_valid_user_form(self):
        form = UserForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation_for_username(self):
        self.form_input['username'] = 'badusername'  # Invalid due to missing '@'
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_form_uses_model_validation_for_email(self):
        self.form_input['email'] = 'invalid-email'  # Invalid email format
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_uses_model_validation_for_role(self):
        self.form_input['role'] = 'invalid_role'  # Not in ROLE_CHOICES
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)

    def test_form_must_save_correctly(self):
        user = User.objects.get(username='@johndoe')
        form = UserForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        saved_user = form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)  # No new user should be created
        self.assertEqual(saved_user.username, '@janedoe')
        self.assertEqual(saved_user.first_name, 'Jane')
        self.assertEqual(saved_user.last_name, 'Doe')
        self.assertEqual(saved_user.email, 'janedoe@example.org')
        self.assertEqual(saved_user.role, 'student')
