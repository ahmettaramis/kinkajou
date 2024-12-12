from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Invoice

class ToggleInvoicePaidTest(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/lesson_requests.json',
        'tutorials/tests/fixtures/invoices.json'
    ]

    def setUp(self):
        self.admin_user = get_user_model().objects.get(username='@johndoe')
        self.client.force_login(self.admin_user)
        self.invoice = Invoice.objects.get(pk=2)
        self.url = reverse('toggle_invoice_paid', kwargs={'invoice_id': self.invoice.id})

    def test_toggle_invoice_paid(self):
        current_is_paid = self.invoice.is_paid
        response = self.client.get(self.url)

        self.invoice.refresh_from_db()
        self.assertRedirects(response, reverse('admin_view_requests'))
        self.assertEqual(self.invoice.is_paid, not current_is_paid)

    def test_toggle_invoice_paid_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/log_in/?next=' + self.url)
