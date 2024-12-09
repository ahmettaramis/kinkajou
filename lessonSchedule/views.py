from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import LessonForm
from tutorials.models import AllocatedLesson

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

@login_required
def tutor_dashboard(request):
    current_user = request.user

    # Check if the logged-in user is a tutor
    if current_user.role == "tutor":
        # Fetch all lessons allocated to this tutor, ordered by date
        allocated_lessons = AllocatedLesson.objects.filter(
            lesson_request__preferred_tutor=current_user
        ).order_by('date')

        # Pass the lessons to the template
        return render(request, 'tutor_dashboard.html', {
            'user': current_user,
            'allocated_lessons': allocated_lessons,
        })

    # Redirect non-tutor users to their respective dashboards
    return redirect('dashboard')
