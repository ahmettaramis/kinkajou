#form for making scheduling

from django import forms
from .models import Lesson

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['tutor', 'student', 'subject', 'venue', 'date', 'time', 'frequency']