"""Unit tests for the Invoice views."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Invoice, LessonRequest
from tutorials.forms import InvoiceForm
from decimal import Decimal

User = get_user_model()

class InvoiceViewTests(TestCase):
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.client = Client()

        self.student = User.objects.get(username='@charlie')
        self.admin = User.objects.get(username='@johndoe')

        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            title="lesson_request",
            description="Request for Django lessons.",
            status="unallocated",
            lesson_date=None,
            preferred_tutor=None,
            no_of_weeks=3
        )

        self.lesson_request1 = LessonRequest.objects.create(
            student=self.student,
            title="lesson_request1",
            description="Request for Django lessons.",
            status="unallocated",
            lesson_date=None,
            preferred_tutor=None,
            no_of_weeks=3
        )

        self.invoice = Invoice.objects.create(
            lesson_request=self.lesson_request,
            amount = Decimal(9999.99),
            is_paid = False
        )

        self.invoice1 = Invoice.objects.create(
            lesson_request=self.lesson_request1,
            amount = Decimal(9999.99),
            is_paid = False
        )

    def test_toggle_invoice_paid(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.get(reverse('toggle_invoice_paid', args=[self.invoice.pk]))

        self.invoice.refresh_from_db()

        self.assertEqual(self.invoice.is_paid, True)
        self.assertRedirects(response, reverse('admin_view_requests'))

    def test_student_view_invoices_authenticated(self):
        self.client.login(username=self.student.username, password='Password123')
        
        url = reverse('student_view_invoices')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        self.assertIn(self.invoice, response.context['invoices'])
        self.assertIn(self.invoice1, response.context['invoices'])

        self.assertTemplateUsed(response, 'student_view_invoices.html')

    def test_student_view_invoices_not_authenticated(self):
        url = reverse('student_view_invoices')
        response = self.client.get(url)

        self.assertRedirects(response, f'/log_in/?next={url}')

    def test_generate_invoice_get(self):
        self.client.login(username=self.admin.username, password='Password123')
        
        url = reverse('generate_invoice', args=[self.lesson_request.pk])
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        
        self.assertIsInstance(response.context['form'], InvoiceForm)
        self.assertEqual(response.context['lesson_request'], self.lesson_request)
        self.assertEqual(response.context['invoice'], self.invoice)
        self.assertTemplateUsed(response, 'generate_invoice.html')

    def test_generate_invoice_post_create(self):
        self.client.login(username=self.admin.username, password='Password123')
        
        new_lesson_request = LessonRequest.objects.create(
            student=self.student,
            title="generate invoice post create",
            description="Request for Django lessons.",
            status="unallocated",
            lesson_date=None,
            preferred_tutor=None,
            no_of_weeks=3
        )
        
        url = reverse('generate_invoice', args=[new_lesson_request.pk])
        form_data = {
            'lesson_request': new_lesson_request.pk,
            'amount': Decimal('150.00'),
            'is_paid': False
        }

        print('generate_invoice_post_create POST')
        response = self.client.post(url, data=form_data)
        created_invoice = Invoice.objects.get(lesson_request=new_lesson_request)

        self.assertEqual(created_invoice.amount, Decimal('150.00'))
        self.assertEqual(created_invoice.is_paid, False)
        self.assertEqual(created_invoice.lesson_request, new_lesson_request)
        self.assertRedirects(response, reverse('admin_view_requests'))

    def test_generate_invoice_post_update(self):
        self.client.login(username=self.admin.username, password='Password123')
        
        url = reverse('generate_invoice', args=[self.lesson_request.pk])
        form_data = {
            'amount': Decimal('200.00'),
            'is_paid': True
        }

        print('generate_invoice_post_update POST')
        response = self.client.post(url, data=form_data)
        updated_invoice = Invoice.objects.get(lesson_request=self.lesson_request)

        self.assertNotEqual(self.invoice.pk, updated_invoice.pk)
        self.assertEqual(updated_invoice.amount, Decimal('200.00'))
        self.assertEqual(updated_invoice.is_paid, True)

        self.assertRedirects(response, reverse('admin_view_requests'))
