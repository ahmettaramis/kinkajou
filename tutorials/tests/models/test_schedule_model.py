from datetime import time
from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, Schedule

class ScheduleModelTestCase(TestCase):
    """Unit tests for the Schedule model."""

    def setUp(self):
        # Create a user for testing schedules
        self.user = User.objects.create_user(username="schedule_user", email="schedule@example.com", password="password")
        
        # Create a valid schedule
        self.schedule = Schedule.objects.create(
            user=self.user,
            day_of_week="Monday",
            start_time=time(10, 0),
            end_time=time(12, 0)
        )

    def test_valid_schedule(self):
        """Test that a valid schedule instance is valid."""
        self._assert_schedule_is_valid()

    def test_schedule_start_time_cannot_be_after_end_time(self):
        """Test that start time cannot be after end time."""
        self.schedule.start_time = time(13, 0)
        self.schedule.end_time = time(12, 0)
        with self.assertRaises(ValidationError):
            self.schedule.full_clean()

    def test_schedule_start_time_can_equal_end_time(self):
        """Test that start time and end time can be equal (zero duration)."""
        self.schedule.start_time = time(12, 0)
        self.schedule.end_time = time(12, 0)
        self._assert_schedule_is_valid()

    def test_schedule_overlap_combines_times(self):
        """Test that overlapping schedules are combined into one."""
        overlapping_schedule = Schedule.objects.create(
            user=self.user,
            day_of_week="Monday",
            start_time=time(11, 0),
            end_time=time(13, 0)
        )
        # Fetch the combined schedule
        combined_schedule = Schedule.objects.filter(user=self.user, day_of_week="Monday").first()

        # Assert the times have been adjusted to encompass the overlap
        self.assertEqual(combined_schedule.start_time, time(10, 0))
        self.assertEqual(combined_schedule.end_time, time(13, 0))

        # Ensure only one schedule remains for the user
        self.assertEqual(Schedule.objects.filter(user=self.user).count(), 1)

    def test_schedule_on_different_days(self):
        """Test that schedules on different days do not overlap."""
        new_schedule = Schedule.objects.create(
            user=self.user,
            day_of_week="Tuesday",
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        # The original schedule should remain unchanged
        self.assertEqual(self.schedule.start_time, time(10, 0))
        self.assertEqual(self.schedule.end_time, time(12, 0))
        
        # Ensure both schedules exist
        self.assertEqual(Schedule.objects.filter(user=self.user).count(), 2)

    def test_schedule_with_different_users(self):
        """Test that schedules for different users are independent."""
        other_user = User.objects.create_user(username="other_user", email="other@example.com", password="password")
        Schedule.objects.create(
            user=other_user,
            day_of_week="Monday",
            start_time=time(11, 0),
            end_time=time(13, 0)
        )

        # Check schedules for the original user
        user_schedules = Schedule.objects.filter(user=self.user, day_of_week="Monday")
        self.assertEqual(user_schedules.count(), 1)
        self.assertEqual(user_schedules.first().start_time, time(10, 0))
        self.assertEqual(user_schedules.first().end_time, time(12, 0))

        # Check schedules for the other user
        other_schedules = Schedule.objects.filter(user=other_user, day_of_week="Monday")
        self.assertEqual(other_schedules.count(), 1)
        self.assertEqual(other_schedules.first().start_time, time(11, 0))
        self.assertEqual(other_schedules.first().end_time, time(13, 0))

    def _assert_schedule_is_valid(self):
        """Helper method to check if a schedule instance is valid."""
        try:
            self.schedule.full_clean()
        except ValidationError:
            self.fail("Schedule should be valid")

    def _assert_schedule_is_invalid(self):
        """Helper method to check if a schedule instance is invalid."""
        with self.assertRaises(ValidationError):
            self.schedule.full_clean()
