"""Unit tests for the admin_view_requests function."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import LessonRequest, Invoice

class AdminViewRequestsTestCase(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/lesson_requests.json',
        'tutorials/tests/fixtures/invoices.json'
    ]

    def setUp(self):
        self.admin_user = get_user_model().objects.get(username='@johndoe')
        self.client.force_login(self.admin_user)
        self.url = reverse('admin_view_requests')

    def test_view_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_view_denies_access_if_not_admin(self):
        tutor_user = get_user_model().objects.get(username='@janedoe')
        self.client.force_login(tutor_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Permission denied

    def test_view_displays_all_requests_by_default(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['requests']), LessonRequest.objects.count())

    def test_view_filters_allocated_requests(self):
        response = self.client.get(self.url, {'filter': 'allocated'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['requests'],
            LessonRequest.objects.filter(status='allocated'),
            transform=lambda x: x
        )

    def test_view_filters_unallocated_requests(self):
        response = self.client.get(self.url, {'filter': 'unallocated'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['requests'],
            LessonRequest.objects.filter(status='unallocated'),
            transform=lambda x: x
        )

    def test_view_filters_paid_requests(self):
        response = self.client.get(self.url, {'filter': 'paid'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['requests'],
            LessonRequest.objects.filter(invoice__is_paid=True),
            transform=lambda x: x
        )

    def test_view_filters_unpaid_requests(self):
        response = self.client.get(self.url, {'filter': 'unpaid'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['requests'],
            LessonRequest.objects.filter(invoice__is_paid=False),
            transform=lambda x: x
        )

    def test_view_filters_requests_with_invoices(self):
        response = self.client.get(self.url, {'filter': 'invoice_generated'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['requests'].order_by('id'),
            LessonRequest.objects.filter(invoice__isnull=False).order_by('id'),
            transform=lambda x: x
        )

    def test_view_filters_requests_without_invoices(self):
        response = self.client.get(self.url, {'filter': 'no_invoice_generated'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['requests'],
            LessonRequest.objects.filter(invoice__isnull=True),
            transform=lambda x: x
        )

    def test_invalid_filter_returns_all_requests(self):
        response = self.client.get(self.url, {'filter': 'invalid_filter'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['requests']), LessonRequest.objects.count())

    def test_view_contains_invoices_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['invoices']), Invoice.objects.count())
