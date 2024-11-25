from django import forms
from .models import lessonSchedule

class LessonForm(forms.ModelForm):
    class Meta:
        model = lessonSchedule
        fields = ['tutor', 'request', 'schedule_time']
        widgets = {
            'schedule_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
