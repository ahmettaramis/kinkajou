from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now, timedelta
from tutorials.models import User, Tutor, LessonRequest, AllocatedLesson, Invoice

class DashboardViewTest(TestCase):
    """
    Combined test suite for the dashboard.
    This includes both the simpler, role-based tests and the more comprehensive tests
    involving allocated lessons, invoices, and edge cases.
    """
    def setUp(self):
        self.client = Client()

        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='@adminuser',
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            role='admin',
            password='Password123'
        )

        self.tutor_user = User.objects.create_user(
            username='@tutoruser',
            first_name='Tutor',
            last_name='User',
            email='tutor@example.com',
            role='tutor',
            password='Password123'
        )
        Tutor.objects.create(user=self.tutor_user, subjects='Python')

        self.student_user = User.objects.create_user(
            username='@studentuser',
            first_name='Student',
            last_name='User',
            email='student@example.com',
            role='student',
            password='Password123'
        )

        # Set up common data for comprehensive tests
        self.future_date = (now() + timedelta(days=5)).date()
        self.lesson_time = (now() + timedelta(hours=1)).time()

        # LessonRequest and AllocatedLesson for student and tutor
        self.lesson_request = LessonRequest.objects.create(
            student_id=self.student_user,
            tutor_id=self.tutor_user,
            language='Python',
            term='Sept-Christmas',
            day_of_the_week='Wednesday',
            frequency='Weekly',
            duration=60,
            status='allocated'
        )

        self.allocated_lesson = AllocatedLesson.objects.create(
            lesson_request=self.lesson_request,
            occurrence=1,
            date=self.future_date,
            time=self.lesson_time,
            language='Python',
            student_id=self.student_user,
            tutor_id=self.tutor_user
        )

        # Unpaid invoice for the student
        self.invoice = Invoice.objects.create(
            lesson_request=self.lesson_request,
            amount='100.00',
            is_paid=False
        )

    # ---------------------------------------
    # Simple Role-Based Template Tests
    # ---------------------------------------
    def test_admin_dashboard_renders_correctly(self):
        """Simple test: Admin sees Admin Dashboard and not the others."""
        self.client.login(username='@adminuser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Dashboard")
        self.assertNotContains(response, "Tutor Dashboard")
        self.assertNotContains(response, "Student Dashboard")
        # Admin does not show lessons or invoice info, so ensure no lesson-related text:
        self.assertNotContains(response, "Your Allocated Lessons")
        self.assertNotContains(response, "You have no allocated lessons at the moment.")

    def test_tutor_dashboard_renders_correctly(self):
        """Simple test: Tutor sees Tutor Dashboard and not the others."""
        self.client.login(username='@tutoruser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tutor Dashboard")
        self.assertNotContains(response, "Admin Dashboard")
        self.assertNotContains(response, "Student Dashboard")

    def test_student_dashboard_renders_correctly(self):
        """Simple test: Student sees Student Dashboard and not the others."""
        self.client.login(username='@studentuser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student Dashboard")
        self.assertNotContains(response, "Admin Dashboard")
        self.assertNotContains(response, "Tutor Dashboard")

    # ---------------------------------------
    # Comprehensive Tests for Student Role
    # ---------------------------------------
    def test_student_dashboard_valid_data(self):
        """
        Comprehensive: Student with allocated lessons and unpaid invoices 
        should see appropriate UI elements.
        """
        self.client.login(username='@studentuser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # Student-specific content & invoices
        self.assertContains(response, 'Student Dashboard')
        self.assertContains(response, 'Submit Lesson Request')
        self.assertContains(response, 'View Your Requests')
        self.assertContains(response, 'View your invoices')
        self.assertContains(response, 'You have 1 unpaid invoice')

        # Allocated lessons table
        self.assertContains(response, 'Your Allocated Lessons')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Cancel')

    def test_student_dashboard_no_lessons(self):
        """Edge case: Student with no allocated lessons."""
        # Create a new student with no lessons
        new_student = User.objects.create_user(
            username='@emptystudent',
            first_name='Empty',
            last_name='Student',
            email='emptystudent@example.com',
            password='Password123',
            role='student'
        )
        self.client.login(username='@emptystudent', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student Dashboard')
        self.assertContains(response, 'You have no allocated lessons at the moment.')

    def test_student_dashboard_no_invoices(self):
        """Edge case: Student with lessons but no unpaid invoices."""
        # Mark existing invoice as paid
        self.invoice.is_paid = True
        self.invoice.save()

        self.client.login(username='@studentuser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # No invoice action needed now
        self.assertNotContains(response, 'You have')

    # ---------------------------------------
    # Comprehensive Tests for Tutor Role
    # ---------------------------------------
    def test_tutor_dashboard_valid_data(self):
        """Tutor with allocated lessons sees tutor dashboard & lesson table."""
        self.client.login(username='@tutoruser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Tutor Dashboard')
        self.assertContains(response, 'Update Availability')
        self.assertContains(response, 'Your Allocated Lessons')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Cancel')
        self.assertNotContains(response, 'invoices')  # Tutor shouldn't see invoices

    def test_tutor_dashboard_no_lessons(self):
        """Tutor with no allocated lessons."""
        empty_tutor = User.objects.create_user(
            username='@emptytutor',
            first_name='NoLessons',
            last_name='Tutor',
            email='emptytutor@example.com',
            password='Password123',
            role='tutor'
        )
        Tutor.objects.create(user=empty_tutor, subjects='Java')

        self.client.login(username='@emptytutor', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tutor Dashboard')
        # Expect a no lessons message for tutors
        self.assertContains(response, 'You have no allocated lessons at the moment.')

    # ---------------------------------------
    # Comprehensive Tests for Admin Role
    # ---------------------------------------
    def test_admin_dashboard_valid_data(self):
        """Admin sees an admin dashboard view. Admins do not have lessons displayed."""
        self.client.login(username='@adminuser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Admin Dashboard')
        self.assertContains(response, 'View All Submitted Requests')
        self.assertContains(response, 'View Tutor List')

        # Since admins do not show lessons, ensure no lesson-related text:
        self.assertNotContains(response, 'Your Allocated Lessons')
        self.assertNotContains(response, 'You have no allocated lessons at the moment.')

    def test_admin_dashboard_no_lessons(self):
        """Admin with no allocated lessons at all. Still, admins do not show any lesson text."""
        AllocatedLesson.objects.all().delete()
        self.client.login(username='@adminuser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Admin Dashboard')
        self.assertNotContains(response, 'Your Allocated Lessons')
        self.assertNotContains(response, 'You have no allocated lessons at the moment.')

    # ---------------------------------------
    # Invalid/Unexpected Role Scenario
    # ---------------------------------------
    def test_unexpected_role_dashboard(self):
        """User with an unexpected role should not display any known dashboard."""
        weird_user = User.objects.create_user(
            username='@weirduser',
            first_name='Weird',
            last_name='User',
            email='weird@example.com',
            password='Password123',
            role='superhero'  # Not a defined role
        )

        self.client.login(username='@weirduser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # No known dashboard text should appear
        self.assertNotContains(response, 'Admin Dashboard')
        self.assertNotContains(response, 'Tutor Dashboard')
        self.assertNotContains(response, 'Student Dashboard')
        # No lesson-related text either
        self.assertNotContains(response, 'Your Allocated Lessons')
        self.assertNotContains(response, 'You have no allocated lessons at the moment.')
