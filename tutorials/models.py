from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
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

class StudentRequest(models.Model):
    pass

class Lesson(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_tutor')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_student')
    description = models.CharField(max_length=255)
    time = models.DateTimeField()

class Invoice(models.Model):

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.01'))])
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)