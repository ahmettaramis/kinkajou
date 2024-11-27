from django.shortcuts import render

# Create your views here.

from django.shortcuts import redirect
from .forms import LessonForm

def schedule_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('schedule-success')
    else:
        form = LessonForm()
    return render(request, 'scheduler/schedule_lesson.html', {'form': form})
