"""Unit tests of the invoice form."""
from django import forms
from django.test import TestCase
from django.utils import timezone
from tutorials.forms import InvoiceForm
from tutorials.models import User, Invoice, LessonRequest
from decimal import Decimal
from django.utils.timezone import now, timedelta

class InvoiceFormTestCase(TestCase):
    """Unit Tests of the Invoice Form"""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]
    
    def setUp(self):
        self.now = now()

        student = User.objects.get(username='@charlie')
        tutor = User.objects.get(username='@janedoe')

        self.lesson_request = LessonRequest.objects.create(
            student_id=student,
            tutor_id=tutor,
            language='Python',
            term='Sept-Christmas',
            day_of_the_week='Monday',
            frequency='Weekly',
            duration=60,
            description='',
            status='Pending',
            date_created = self.now
        )
        
        self.form_input = {
            'lesson_request' : self.lesson_request,
            'amount' : 9999.99,
            'is_paid' : False
        }

    def test_form_has_necessary_fields(self):
        form = InvoiceForm()
        self.assertIn('lesson_request', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('is_paid', form.fields)

    def test_valid_invoice_form(self):
        form = InvoiceForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_must_save_correctly(self):
        invoice = Invoice.objects.create(lesson_request=self.lesson_request, amount=9999.99, is_paid=False)
        form = InvoiceForm(instance=invoice, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(invoice.lesson_request, self.lesson_request)
        self.assertEqual(invoice.amount, Decimal('9999.99'))
        self.assertEqual(invoice.is_paid, False)