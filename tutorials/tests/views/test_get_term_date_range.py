import os
import unittest
from datetime import datetime
from django.conf import settings
from django.test import TestCase

# Set the settings module for testing
os.environ['DJANGO_SETTINGS_MODULE'] = 'tutorials.settings'

# Now import your views or models
from tutorials.views import get_term_date_range  # Adjusted import path

class TestGetTermDateRange(TestCase):
    def setUp(self):
        # Common test year for simplicity
        self.test_year = 2024

    def test_valid_terms_within_year(self):
        # Sept-Christmas
        lower, upper = get_term_date_range('Sept-Christmas', datetime(self.test_year, 8, 31))
        self.assertEqual(lower, datetime(self.test_year, 9, 1))
        self.assertEqual(upper, datetime(self.test_year, 12, 25))

        # Jan-Easter
        lower, upper = get_term_date_range('Jan-Easter', datetime(self.test_year, 12, 31))
        self.assertEqual(lower, datetime(self.test_year + 1, 1, 1))
        self.assertEqual(upper, datetime(self.test_year + 1, 4, 15))

        # March-June
        lower, upper = get_term_date_range('March-June', datetime(self.test_year, 2, 28))
        self.assertEqual(lower, datetime(self.test_year, 3, 1))
        self.assertEqual(upper, datetime(self.test_year, 6, 30))

    def test_term_transition_to_next_year(self):
        # Sept-Christmas when created after December 25
        lower, upper = get_term_date_range('Sept-Christmas', datetime(self.test_year, 12, 26))
        self.assertEqual(lower, datetime(self.test_year + 1, 9, 1))
        self.assertEqual(upper, datetime(self.test_year + 1, 12, 25))

        # Jan-Easter when created after April 15
        lower, upper = get_term_date_range('Jan-Easter', datetime(self.test_year, 4, 16))
        self.assertEqual(lower, datetime(self.test_year + 1, 1, 1))
        self.assertEqual(upper, datetime(self.test_year + 1, 4, 15))

        # March-June when created after June 30
        lower, upper = get_term_date_range('March-June', datetime(self.test_year, 7, 1))
        self.assertEqual(lower, datetime(self.test_year + 1, 3, 1))
        self.assertEqual(upper, datetime(self.test_year + 1, 6, 30))

    def test_term_on_boundary_dates(self):
        # Sept-Christmas on December 25
        lower, upper = get_term_date_range('Sept-Christmas', datetime(self.test_year, 12, 25))
        self.assertEqual(lower, datetime(self.test_year, 9, 1))
        self.assertEqual(upper, datetime(self.test_year, 12, 25))

        # Jan-Easter on April 15
        lower, upper = get_term_date_range('Jan-Easter', datetime(self.test_year, 4, 15))
        self.assertEqual(lower, datetime(self.test_year, 1, 1))
        self.assertEqual(upper, datetime(self.test_year, 4, 15))

        # March-June on June 30
        lower, upper = get_term_date_range('March-June', datetime(self.test_year, 6, 30))
        self.assertEqual(lower, datetime(self.test_year, 3, 1))
        self.assertEqual(upper, datetime(self.test_year, 6, 30))

    def test_invalid_term(self):
        with self.assertRaises(ValueError) as context:
            get_term_date_range('Invalid-Term', datetime(self.test_year, 1, 1))
        self.assertEqual(str(context.exception), "Unknown term: Invalid-Term")

    def test_invalid_date_created_type(self):
        with self.assertRaises(TypeError) as context:
            get_term_date_range('Sept-Christmas', "2024-09-01")
        self.assertEqual(str(context.exception), "date_created must be a datetime object")

        with self.assertRaises(TypeError) as context:
            get_term_date_range('Sept-Christmas', None)
        self.assertEqual(str(context.exception), "date_created must be a datetime object")

    def test_timezone_handling(self):
        from pytz import timezone
        tz = timezone('GMT')
        date_with_tz = tz.localize(datetime(self.test_year, 12, 26))

        lower, upper = get_term_date_range('Sept-Christmas', date_with_tz)
        self.assertEqual(lower, datetime(self.test_year + 1, 9, 1))  # Should remove tzinfo
        self.assertEqual(upper, datetime(self.test_year + 1, 12, 25))

        # Ensure no timezone info remains in the results
        self.assertIsNone(lower.tzinfo)
        self.assertIsNone(upper.tzinfo)
