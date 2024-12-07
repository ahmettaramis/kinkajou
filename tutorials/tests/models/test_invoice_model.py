"""Unit tests for the Invoice model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from tutorials.models import Invoice, Lesson, User

class InvoiceModelTestCase(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        student = User.objects.get(username='@charlie')
        tutor = User.objects.get(username='@janedoe')

        lesson = Lesson.objects.create(tutor=tutor, student=student, description='test description.', time=timezone.now())
        self.invoice = Invoice.objects.create(lesson=lesson, amount=9999.99, is_paid=False, created_at=timezone.now())

    def test_valid_invoice(self):
        self._assert_invoice_is_valid()

    def test_amount_cannot_be_zero(self):
        self.invoice.amount = 0
        self._assert_invoice_is_invalid()

    def test_amount_cannot_be_negative(self):
        self.invoice.amount = -0.1
        self._assert_invoice_is_invalid()

    def test_amount_cannot_be_too_large(self):
        self.invoice.amount = 99999.99
        self._assert_invoice_is_invalid()

    def test_amount_cannot_have_too_many_decimals(self):
        self.invoice.amount = 9.999
        self._assert_invoice_is_invalid()

    def _assert_invoice_is_valid(self):
        try:
            self.invoice.full_clean()
        except (ValidationError):
            self.fail('Test invoice should be valid')

    def _assert_invoice_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()