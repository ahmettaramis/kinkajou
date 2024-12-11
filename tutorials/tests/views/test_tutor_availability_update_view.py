"""Tests for TutorAvailabilityUpdateView."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor, Schedule, User

class TutorAvailabilityUpdateViewTestCase(TestCase):
    """Tests for the TutorAvailabilityUpdateView."""

    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username='@janedoe',
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            role='tutor',
            password='Password123'
        )
        self.student_user = User.objects.create_user(
            username='@charlie',
            first_name='Charlie',
            last_name='Johnson',
            email='charlie.johnson@example.com',
            role='student',
            password='Password123'
        )
        self.tutor_profile = Tutor.objects.create(user=self.tutor_user, subjects='python')
        self.schedule = Schedule.objects.create(
            user=self.tutor_user,
            day_of_week='Monday',
            start_time='10:00:00',
            end_time='12:00:00'
        )
        self.url = reverse('update_schedule')

    def test_tutor_can_access_availability_view(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_schedule.html')
        self.assertIn('availability', response.context)
        self.assertIn('form', response.context)

    def test_non_tutor_redirected(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home'), status_code=302, target_status_code=200)

    def test_schedule_creation(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {
            'day_of_week': 'Tuesday',
            'start_time': '09:00',
            'end_time': '11:00'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(Schedule.objects.filter(user=self.tutor_user, day_of_week='Tuesday').count(), 1)
        self.assertRedirects(response, self.url)

    def test_schedule_deletion(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {
            'delete_schedule': self.schedule.id
        }
        response = self.client.post(self.url, data)
        self.assertFalse(Schedule.objects.filter(id=self.schedule.id).exists())
        self.assertRedirects(response, self.url)

    def test_schedule_sorting(self):
        self.client.login(username='@janedoe', password='Password123')
        Schedule.objects.create(
            user=self.tutor_user,
            day_of_week='Wednesday',
            start_time='09:00:00',
            end_time='11:00:00'
        )
        response = self.client.get(self.url)
        schedules = response.context['availability']
        self.assertEqual(schedules[0].day_of_week, 'Monday')
        self.assertEqual(schedules[1].day_of_week, 'Wednesday')
