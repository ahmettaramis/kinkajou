from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
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
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')


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
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor_profile')
    
    expertise = models.CharField(max_length=200, blank=True, null=True)
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
