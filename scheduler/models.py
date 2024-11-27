from django.db import models
from django.conf import settings

class Tutor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Lesson(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    venue = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    frequency = models.CharField(max_length=50, choices=[('Weekly', 'Weekly'), ('Fortnightly', 'Fortnightly')])

    def __str__(self):
        return f"{self.subject} with {self.tutor.user.username} - {self.student.user.username}"