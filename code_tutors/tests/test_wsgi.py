"""
Test for WSGI config in the code_tutors project.
"""

import os
import unittest
from django.core.wsgi import get_wsgi_application


class TestWSGIConfig(unittest.TestCase):
    def test_wsgi_application_initialization(self):
        # Set the default settings module for the project
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'code_tutors.settings')

        try:
            application = get_wsgi_application()
            self.assertIsNotNone(application, "WSGI application should not be None.")
        except Exception as e:
            self.fail(f"WSGI application failed to initialize. Error: {e}")