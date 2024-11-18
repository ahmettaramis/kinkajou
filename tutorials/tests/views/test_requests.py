from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from tutorials.models import StudentRequest

User = get_user_model()

class StudentRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_create_request(self):
        response = self.client.post(reverse('create_request'), {
            'title': 'Test Request',
            'description': 'This is a test request.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(StudentRequest.objects.count(), 1)
        self.assertEqual(StudentRequest.objects.first().title, 'Test Request')
