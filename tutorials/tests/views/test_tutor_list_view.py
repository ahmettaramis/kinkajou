from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import User, Tutor, Schedule
from datetime import time

class TutorListViewTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='password',
            role='admin'
        )
        self.student_user = User.objects.create_user(
            username='student_user',
            email='student@example.com',
            password='password',
            role='student'
        )
        self.tutor_user_1 = User.objects.create_user(
            username='tutor_user_1',
            email='tutor1@example.com',
            password='password',
            role='tutor'
        )
        self.tutor_1 = Tutor.objects.create(user=self.tutor_user_1, subjects='Python')
        Schedule.objects.create(
            user=self.tutor_user_1,
            day_of_week='Monday',
            start_time=time(9, 0),
            end_time=time(11, 0)
        )
        self.tutor_user_2 = User.objects.create_user(
            username='tutor_user_2',
            email='tutor2@example.com',
            password='password',
            role='tutor'
        )
        self.tutor_2 = Tutor.objects.create(user=self.tutor_user_2, subjects='Java')
        Schedule.objects.create(
            user=self.tutor_user_2,
            day_of_week='Tuesday',
            start_time=time(13, 0),
            end_time=time(15, 0)
        )
        self.client = Client()

    def test_filter_by_day(self):
        self.client.login(username='admin_user', password='password')
        response = self.client.get(reverse('tutor_list_view') + '?day=Monday')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Monday: 09:00 - 11:00')

    def test_filter_by_subject(self):
        self.client.login(username='admin_user', password='password')
        response = self.client.get(reverse('tutor_list_view') + '?subjects=Python')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Monday: 09:00 - 11:00')

    def test_no_filters_applied(self):
        self.client.login(username='admin_user', password='password')
        response = self.client.get(reverse('tutor_list_view') + '?subjects=any&day=any')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Monday: 09:00 - 11:00')
        self.assertContains(response, 'Java')
        self.assertContains(response, 'Tuesday: 13:00 - 15:00')

    def test_redirect_non_admin_user(self):
        self.client.login(username='student_user', password='password')
        response = self.client.get(reverse('tutor_list_view'), follow=True)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_access_by_admin_user(self):
        self.client.login(username='admin_user', password='password')
        response = self.client.get(reverse('tutor_list_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Available Tutors')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Java')

    def test_filter_by_subject_and_day(self):
        self.client.login(username='admin_user', password='password')
        response = self.client.get(reverse('tutor_list_view') + '?subjects=Python&day=Monday')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Monday: 09:00 - 11:00')
