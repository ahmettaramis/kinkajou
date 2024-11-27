from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class LessonRequest(models.Model):
    """Model for lesson requests made by students."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_requests'
    )
    topic = models.CharField(max_length=255)
    preferred_time = models.DateTimeField()
    status = models.CharField(max_length=50, default="Pending")  # E.g., Pending, Approved
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.student.username} for {self.topic}"
    

class Lesson(models.Model):
    """Model for scheduled lessons."""
    schedule_time = models.DateTimeField()
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutored_lessons'
    )
    request = models.ForeignKey(
        LessonRequest,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    def __str__(self):
        return f"Lesson for {self.request.topic} with {self.tutor.username}"
    
class Invoice(models.Model):
    """Model for lesson invoices."""
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='invoices'
    )

    def __str__(self):
        return f"Invoice for {self.lesson.request.topic} - {self.amount} USD"

class TutorAvailability(models.Model):
    """Model for tutor availability."""
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    available_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tutor.username} - {'Booked' if self.is_booked else 'Available'}"



