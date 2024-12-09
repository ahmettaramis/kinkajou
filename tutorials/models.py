from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now, timedelta

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
        return f'{self.user.username} - {self.expertise}'

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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')  # For both students and tutors
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.user.username}: {self.day_of_week} {self.start_time}-{self.end_time}"


User = get_user_model()

# class LessonRequest(models.Model):
#     # Fields
#     student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_requests")
#     title = models.CharField(max_length=255)
#     description = models.TextField(max_length=1000)
#     status = models.CharField(
#         max_length=50,
#         choices=[('unallocated', 'Unallocated'), ('allocated', 'Allocated')],
#         default='unallocated'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     lesson_date = models.DateTimeField(null=True, blank=True)
#     preferred_tutor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="preferred_requests")
#     no_of_weeks = models.PositiveIntegerField()
#
#     def clean(self):
#         # Validate date is not in the past
#         if self.lesson_date and self.lesson_date < now():
#             raise ValidationError("Lesson date cannot be in the past.")
#         # Validate number of weeks
#         if self.no_of_weeks < 1 or self.no_of_weeks > 52:
#             raise ValidationError("Number of weeks must be between 1 and 52.")
#         # Ensure a tutor is assigned when allocating
#         if self.status == 'allocated' and not self.preferred_tutor:
#             raise ValidationError("A tutor must be assigned for allocated lessons.")
#
#     def __str__(self):
#         return f"{self.title} ({self.status})"
#
#     def allocate_lessons(self):
#         # Create allocated lessons for this request based on no_of_weeks.
#         if self.status == 'allocated' and self.lesson_date and self.no_of_weeks:
#             AllocatedLesson.objects.filter(lesson_request=self).delete()  # Ensure no duplicates
#             for i in range(self.no_of_weeks):
#                 AllocatedLesson.objects.create(
#                     lesson_request=self,
#                     occurrence=i + 1,
#                     date=self.lesson_date + timedelta(weeks=i)
#                 )
#
#     def unallocate_lessons(self):
#         # Remove all allocated lessons for this request.
#         if self.status == 'unallocated':
#             AllocatedLesson.objects.filter(lesson_request=self).delete()
#
#     def save(self, *args, **kwargs):
#         # Override save to handle allocation logic.
#         old_status = LessonRequest.objects.filter(pk=self.pk).first()
#         old_status = old_status.status if old_status else None
#         super().save(*args, **kwargs)
#
#         # Automatically manage allocated lessons based on status change
#         if self.status == 'allocated' and old_status != 'allocated':
#             self.allocate_lessons()
#         elif self.status == 'unallocated' and old_status != 'unallocated':
#             self.unallocate_lessons()

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
        (15, '15 minutes'),
        (30, '30 minutes'),
        (45, '45 minutes'),
        (60, '60 minutes'),
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
    date = models.DateTimeField()
    duration = models.IntegerField()  # Duration in minutes, inherited from LessonRequest

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