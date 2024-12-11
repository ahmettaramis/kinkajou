"""Unit tests of the invoice form."""
from django import forms
from django.test import TestCase
from django.utils import timezone
from tutorials.forms import InvoiceForm
from tutorials.models import User, Invoice, Lesson
from decimal import Decimal
import datetime

class InvoiceFormTestCase(TestCase):
    """Unit Tests of the Invoice Form"""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]
    
    def setUp(self):
        self.now = datetime.datetime(2024, 12, 4, 14, 31, 28, 543326, tzinfo=datetime.timezone.utc)

        student = User.objects.get(username='@charlie')
        tutor = User.objects.get(username='@janedoe')

        self.lesson = Lesson.objects.create(tutor=tutor, student=student, description='test description.', time=self.now)

        self.form_input = {
            'lesson' : self.lesson,
            'amount' : 9999.99,
            'is_paid' : False,
            'created_at' : self.now
        }

    def test_form_has_necessary_fields(self):
        form = InvoiceForm()
        self.assertIn('lesson', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('is_paid', form.fields)

    def test_valid_invoice_form(self):
        form = InvoiceForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_must_save_correctly(self):
        invoice = Invoice.objects.create(lesson=self.lesson, amount=9999.99, is_paid=False, created_at=self.now)
        form = InvoiceForm(instance=invoice, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(invoice.lesson, self.lesson)
        self.assertEqual(invoice.amount, Decimal('9999.99'))
        self.assertEqual(invoice.is_paid, False)
        self.assertEqual(invoice.created_at, self.now)