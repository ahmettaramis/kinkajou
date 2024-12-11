from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from tutorials.models import Invoice, LessonRequest, User
import datetime
from django.utils.timezone import now


class InvoiceModelTest(TestCase):
    
    def setUp(self):
        """
        Set up data for the test case. This runs before each test method.
        """
        self.now = now()
        
        student = User.objects.create(username='@charlie', email='charlie@example.com')
        tutor = User.objects.create(username='@janedoe', email='janedoe@example.com')

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
        
        self.invoice_data = {
            'lesson_request': self.lesson_request,
            'amount': Decimal('9999.99'),
            'is_paid': False,
            'created_at': self.now
        }

    """Test creating an Invoice instance"""
    def test_invoice_creation(self):
        invoice = Invoice.objects.create(**self.invoice_data)

        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.lesson_request, self.lesson_request)
        self.assertEqual(invoice.amount, Decimal('9999.99'))
        self.assertEqual(invoice.is_paid, False)
        self.assertEqual(invoice.created_at.date(), self.now.date()) 
        self.assertIsInstance(invoice.created_at, datetime.datetime)

    """Test that the `created_at` field is set automatically on creation"""
    def test_invoice_default_created_at(self):
        invoice = Invoice.objects.create(
            lesson_request=self.lesson_request,
            amount=Decimal('500.00'),
            is_paid=True
        )
        
        self.assertIsNotNone(invoice.created_at)
        self.assertEqual(invoice.created_at.date(), timezone.now().date())

    """Test that an invalid amount (less than 0.01) raises a validation error"""
    def test_invoice_invalid_amount(self):
        invoice = Invoice(lesson_request=self.lesson_request, amount=Decimal('0.00'), is_paid=False)
        
        with self.assertRaises(ValidationError):
            invoice.full_clean() 
            invoice.save() 

    """Test the relationship between Invoice and LessonRequest"""      
    def test_invoice_relationship_with_lesson_request(self):
        invoice = Invoice.objects.create(**self.invoice_data)

        self.assertIn(invoice, self.lesson_request.invoice.all())

    """Test that the default value of `is_paid` is set to False"""
    def test_invoice_is_paid_default(self):
        invoice = Invoice.objects.create(
            lesson_request=self.lesson_request,
            amount=Decimal('500.00'),
        )

        self.assertEqual(invoice.is_paid, False)

    """Test that `created_at` field has `auto_now_add=True` behavior"""
    def test_invoice_created_at_auto_now_add(self):
        invoice = Invoice.objects.create(
            lesson_request=self.lesson_request,
            amount=Decimal('250.00'),
            is_paid=False
        )

        self.assertIsNotNone(invoice.created_at)
        self.assertTrue(invoice.created_at <= timezone.now())

