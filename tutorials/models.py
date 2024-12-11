from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now, timedelta

from django.core.validators import MinValueValidator
from decimal import Decimal
from libgravatar import Gravatar

from code_tutors import settings


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
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('C++', 'C++'),
        ('Scala', 'Scala'),
        ('R', 'R'),
        ('Javascript', 'Javascript'),
        ('Swift', 'Swift'),
        ('Go', 'Go'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor_profile')

    subjects = models.CharField(max_length=50, choices=TOPICS, blank=True, null=True)

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
    LANGUAGE_CHOICES = [
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('C++', 'C++'),
        ('Scala', 'Scala'),
        ('R', 'R'),
        ('Javascript', 'Javascript'),
        ('Swift', 'Swift'),
        ('Go', 'Go'),
    ]

    TERM_CHOICES = [
        ('Sept-Christmas', 'Sept-Christmas'),
        ('Jan-Easter', 'Jan-Easter'),
        ('March-June', 'March-June'),
    ]

    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    FREQUENCY_CHOICES = [
        ('Weekly', 'Weekly'),
        ('Bi-Weekly', 'Bi-Weekly'),
        ('Monthly', 'Monthly'),
    ]

    DURATION_CHOICES = [
        (60, '60 minutes'),
        (120, '120 minutes'),
    ]

    student_id = models.ForeignKey('tutorials.User', on_delete=models.CASCADE, related_name='lesson_requests_as_student')
    tutor_id = models.ForeignKey('tutorials.User', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='lesson_requests_as_tutor')
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    day_of_the_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    duration = models.IntegerField(choices=DURATION_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='Pending')
    date_created = models.DateTimeField(default=now)

    def __str__(self):
        return f"Request by {self.student_id} for {self.language}"

class AllocatedLesson(models.Model):
    lesson_request = models.ForeignKey(
        'LessonRequest',
        on_delete=models.CASCADE,
        related_name='allocated_lessons'
    )
    occurrence = models.PositiveIntegerField()
    date = models.DateField()
    time = models.TimeField()
    language = models.CharField(max_length=100)
    student_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='allocated_lessons_as_student'  # Custom related_name to avoid conflict
    )
    tutor_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='allocated_lessons_as_tutor'  # Custom related_name to avoid conflict
    )

    class Meta:
        unique_together = ('lesson_request', 'occurrence')

    def __str__(self):
        return f"Lesson Request {self.lesson_request.id} - Occurrence {self.occurrence} on {self.date}"

    def clean(self):
        """
        Ensures that the allocated lesson's date is within the lesson request's constraints.
        """
        if self.date < now():
            raise ValidationError("Allocated lesson date cannot be in the past.")
        super().clean()

class Invoice(models.Model):

    lesson_request = models.ForeignKey(LessonRequest, on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.01'))])
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
