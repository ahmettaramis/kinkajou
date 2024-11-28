"""Unit tests for the LessonRequest form."""

from django import forms
from django.test import TestCase
from django.utils.timezone import now, timedelta
from tutorials.forms import LessonRequestForm
from tutorials.models import User, LessonRequest


class LessonRequestFormTestCase(TestCase):
    """Unit tests for the LessonRequest form."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_lesson_requests.json',
        'tutorials/tests/fixtures/other_lesson_requests.json',
    ]

    def setUp(self):
        self.admin = User.objects.get(username='@janedoe')  # Admin only
        self.tutor = User.objects.get(username='@petrapickles')  # Tutor only
        self.student = User.objects.get(username='@peterpickles')  # Student only
        self.admin_tutor = User.objects.get(username='@johndoe')  # Admin and Tutor

        self.form_input = {
            'title': "Learn Python",
            'description': "A lesson request for beginner Python programming.",
            'lesson_date': (now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
            'preferred_tutor': self.tutor.id,
        }

    """Unit tests for student in LessonRequest form."""

    def test_student_can_submit_lesson_request(self):
        form = LessonRequestForm(data=self.form_input)
        form.instance.student = self.student
        self.assertTrue(form.is_valid())

    def test_tutor_cannot_submit_lesson_request(self):
        form = LessonRequestForm(data=self.form_input)
        form.instance.student = self.tutor
        self.assertFalse(form.is_valid())

    def test_admin_cannot_submit_lesson_request(self):
        form = LessonRequestForm(data=self.form_input)
        form.instance.student = self.admin
        self.assertFalse(form.is_valid())

    def test_admin_and_tutor_cannot_submit_lesson_request(self):
        form = LessonRequestForm(data=self.form_input)
        form.instance.student = self.admin_tutor
        self.assertFalse(form.is_valid())

    """Unit tests for title in LessonRequest form."""

    def test_title_cannot_be_empty(self):
        self.form_input['title'] = ''
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_title_cannot_exceed_255_characters(self):
        self.form_input['title'] = 'x' * 256
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_title_can_be_255_characters(self):
        self.form_input['title'] = 'x' * 255
        form = LessonRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    """Unit tests for lesson_date in LessonRequest form."""

    def test_lesson_date_can_be_in_the_future(self):
        self.form_input['lesson_date'] = (now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')
        form = LessonRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_lesson_date_cannot_be_in_the_past(self):
        self.form_input['lesson_date'] = (now() - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    """Unit tests for preferred_tutor in LessonRequest form."""

    def test_student_cannot_be_preferred_tutor(self):
        self.form_input['preferred_tutor'] = self.student.id
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_tutor_can_be_preferred_tutor(self):
        self.form_input['preferred_tutor'] = self.tutor.id
        form = LessonRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_admin_cannot_be_preferred_tutor(self):
        self.form_input['preferred_tutor'] = self.admin.id
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_admin_and_tutor_can_be_preferred_tutor(self):
        self.form_input['preferred_tutor'] = self.admin_tutor.id
        form = LessonRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_save_creates_lesson_request(self):
        form = LessonRequestForm(data=self.form_input)
        form.instance.student = self.student
        if form.is_valid():
            lesson_request = form.save(commit=False)
            lesson_request.save()
            self.assertEqual(lesson_request.title, self.form_input['title'])
            self.assertEqual(lesson_request.description, self.form_input['description'])
            self.assertEqual(lesson_request.lesson_date.strftime('%Y-%m-%dT%H:%M'), self.form_input['lesson_date'])
            self.assertEqual(lesson_request.preferred_tutor, self.tutor)
