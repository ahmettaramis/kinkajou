from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import LessonForm

@login_required
def create_lesson(request):
    """View to create a new lesson."""
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Replace with your redirect target
    else:
        form = LessonForm()

    # Updated template reference
    return render(request, 'lessonSchedule/create_lesson.html', {'form': form})
