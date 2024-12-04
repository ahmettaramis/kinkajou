from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

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

    def __str__(self):
        return f"{self.title} ({self.status})"
