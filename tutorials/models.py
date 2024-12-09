from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now, timedelta

from django.core.validators import MinValueValidator
from decimal import Decimal
from libgravatar import Gravatar

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('tutor', 'Tutor'),
        ('student', 'Student'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='Role'
    )

    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)

class Tutor(models.Model):
    """Model for tutors, extending User"""

    TOPICS = [
    ('algorithms', 'Algorithms'),
    ('databases', 'Databases'),
    ('web', 'Web'),
    ('networks', 'Networks'),
    ('security', 'Security'),
    ('ai', 'AI'),
    ('logic', 'Logic'),
    ('python', 'Python'),
    ('java', 'Java'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor_profile')

    subjects = models.CharField(max_length=50, choices=TOPICS, blank=True, null=True)
    availability = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.subjects}'

class Student(models.Model):
    """Model for students, extending User"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    tutor = models.ForeignKey('Tutor', related_name='students',
                              on_delete=models.SET_NULL, null = True, blank = True)

    def __str__(self):
        return f"{self.user.username}"

class Schedule(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    user = models.ForeignKey(User,
                            on_delete=models.CASCADE,
                            related_name='schedules',
                            null=False,
                            blank=False)
    
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.user.username}: {self.day_of_week} {self.start_time}-{self.end_time}"
    
    def clean(self):
        if self.start_time > self.end_time:
            raise ValidationError("Start time cannot be after end time.")
    
    def save(self, *args, **kwargs):
        # Filter for overlapping schedules for the same user and same day
        overlapping_schedules = Schedule.objects.filter(
            user=self.user,  # Restrict to the same user
            day_of_week=self.day_of_week  # Restrict to the same day
        ).exclude(id=self.id)  # Exclude the current instance

        # Find overlaps
        overlapping_schedules = [
            schedule for schedule in overlapping_schedules
            if schedule.start_time <= self.end_time and schedule.end_time >= self.start_time
        ]

        if overlapping_schedules:
            # Adjust the start and end time to encompass all overlaps
            for schedule in overlapping_schedules:
                self.start_time = min(self.start_time, schedule.start_time)
                self.end_time = max(self.end_time, schedule.end_time)
                # Delete the overlapping schedules
                schedule.delete()

        #save new shcedule
        super().save(*args, **kwargs)



User = get_user_model()

class LessonRequest(models.Model):
    # Fields
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_requests")
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    status = models.CharField(
        max_length=50,
        choices=[('unallocated', 'Unallocated'), ('allocated', 'Allocated')],
        default='unallocated'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    lesson_date = models.DateTimeField(null=True, blank=True)
    preferred_tutor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="preferred_requests")
    no_of_weeks = models.PositiveIntegerField()

    def clean(self):
        # Validate date is not in the past
        if self.lesson_date and self.lesson_date < now():
            raise ValidationError("Lesson date cannot be in the past.")
        # Validate number of weeks
        if self.no_of_weeks < 1 or self.no_of_weeks > 52:
            raise ValidationError("Number of weeks must be between 1 and 52.")
        # Ensure a tutor is assigned when allocating
        if self.status == 'allocated' and not self.preferred_tutor:
            raise ValidationError("A tutor must be assigned for allocated lessons.")

    def __str__(self):
        return f"{self.title} ({self.status})"
    
    def allocate_lessons(self):
        # Create allocated lessons for this request based on no_of_weeks.
        if self.status == 'allocated' and self.lesson_date and self.no_of_weeks:
            AllocatedLesson.objects.filter(lesson_request=self).delete()  # Ensure no duplicates
            for i in range(self.no_of_weeks):
                AllocatedLesson.objects.create(
                    lesson_request=self,
                    occurrence=i + 1,
                    date=self.lesson_date + timedelta(weeks=i)
                )

    def unallocate_lessons(self):
        # Remove all allocated lessons for this request.
        if self.status == 'unallocated':
            AllocatedLesson.objects.filter(lesson_request=self).delete()

    def save(self, *args, **kwargs):
        # Override save to handle allocation logic.
        old_status = LessonRequest.objects.filter(pk=self.pk).first()
        old_status = old_status.status if old_status else None
        super().save(*args, **kwargs)

        # Automatically manage allocated lessons based on status change
        if self.status == 'allocated' and old_status != 'allocated':
            self.allocate_lessons()
        elif self.status == 'unallocated' and old_status != 'unallocated':
            self.unallocate_lessons()

class AllocatedLesson(models.Model):
    lesson_request = models.ForeignKey(
        'LessonRequest',
        on_delete=models.CASCADE,
        related_name='allocated_lessons'
    )
    occurrence = models.PositiveIntegerField()
    date = models.DateTimeField()

    class Meta:
        unique_together = ('lesson_request', 'occurrence')

    def __str__(self):
        return f"Lesson {self.lesson_request.id} - Occurrence {self.occurrence} on {self.date}"

class Invoice(models.Model):

    lesson_request = models.ForeignKey(LessonRequest, on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.01'))])
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)