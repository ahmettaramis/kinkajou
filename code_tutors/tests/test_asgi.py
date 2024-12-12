"""
Test for ASGI config in the code_tutors project.
"""

import os
import unittest
from django.core.asgi import get_asgi_application


class TestASGIConfig(unittest.TestCase):
    def test_asgi_application_initialization(self):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'code_tutors.settings')

        try:
            application = get_asgi_application()
            self.assertIsNotNone(application, "ASGI application should not be None.")
        except Exception as e:
            self.fail(f"ASGI application failed to initialize. Error: {e}")