from django.shortcuts import render

# Create your views here.

from django.shortcuts import redirect
from .forms import LessonForm

def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():  # `is_valid()` is a built-in method for Django forms to validate input
            form.save()
            return redirect('lesson-success')  # Redirect to a success page after saving
    else:
        form = LessonForm()
    return render(request, 'scheduler/create_lesson.html', {'form': form})