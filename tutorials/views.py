from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.db.models import Prefetch
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from .models import User, Tutor, Schedule
from .forms import ScheduleForm

from .models import LessonRequest, AllocatedLesson
from .forms import LessonRequestForm
from .helpers import *
from django.core.exceptions import PermissionDenied


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    allocated_lessons = AllocatedLesson.objects.filter(lesson_request__student=current_user)
    return render(request, 'dashboard.html', {'user': current_user, 'allocated_lessons': allocated_lessons})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

User = get_user_model()

# Student: Submit Lesson Request
@login_required
@is_student
def create_lesson_request(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            lesson_request = form.save(commit=False)
            lesson_request.student = request.user
            lesson_request.save()
            return redirect('student_view_requests')
    else:
        form = LessonRequestForm()
    return render(request, 'lesson_requests/create_request.html', {'form': form})

# Student: View Own Requests
@login_required
@is_student
def student_view_requests(request):
    requests = LessonRequest.objects.filter(student=request.user)
    return render(request, 'lesson_requests/student_view_requests.html', {'requests': requests})

# Admin: View All Requests
@login_required
@is_student
def admin_view_requests(request):
    status_filter = request.GET.get('status')  # Get status filter from query params
    if status_filter:
        requests = LessonRequest.objects.filter(status=status_filter)
    else:
        requests = LessonRequest.objects.all()
    return render(request, 'lesson_requests/admin_view_requests.html', {'requests': requests})

# Admin: Update Request Status
@login_required
@is_student
def update_request_status(request, pk):
    lesson_request = get_object_or_404(LessonRequest, pk=pk)
    tutors = User.objects.filter(role = "tutor")

    if request.method == 'POST':
        new_status = request.POST.get('status')
        selected_tutor_id = request.POST.get('preferred_tutor')

        # Validate that a tutor is selected if allocating
        if new_status == 'allocated' and not selected_tutor_id:
            messages.error(request, "You must assign a tutor before allocating the lesson.")
        else:
            # Assign the tutor if provided
            if selected_tutor_id:
                tutor = User.objects.get(id=selected_tutor_id)
                lesson_request.preferred_tutor = tutor
            
            # Update the status
            lesson_request.status = new_status
            lesson_request.save()

            # Redirect with a success message
            messages.success(request, f"Lesson request status updated to '{new_status}'.")
            return redirect('admin_view_requests')

    return render(request, 'lesson_requests/update_request_status.html', {
        'lesson_request': lesson_request,
        'tutors': tutors
    })

    

class TutorListView(ListView):
    """View to display all tutors."""
    
    model = Tutor  
    template_name = 'tutor_list.html' 
    context_object_name = 'tutors'

    def get_queryset(self):
        queryset = Tutor.objects.prefetch_related(
            Prefetch(
                'user__schedules',
                queryset=Schedule.objects.order_by('day_of_week', 'start_time'),
                to_attr='available_schedules'
            )
        )

        # Get search parameters
        subjects = self.request.GET.get('subjects', 'any')
        day = self.request.GET.get('day', 'any')

        # Filter by subject
        if subjects != "any":
            queryset = queryset.filter(subjects=subjects)

        # Filter by day
        if day != "any":
            queryset = queryset.filter(user__schedules__day_of_week__iexact=day)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        """Provide context for populating dropdowns."""
        context = super().get_context_data(**kwargs)
        context['subjects'] = Tutor.TOPICS  # Pass subjects to the template
        context['days'] = Schedule.DAYS_OF_WEEK  # Pass days to the template
        return context



class TutorAvailabilityUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'update_schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tutor = get_object_or_404(Tutor, user=self.request.user)

        #implement a 403?
        """ if self.request.user.role != 'tutor':
            raise PermissionDenied("You do not have permission to access this page.") """
        
        context['availability'] = Schedule.objects.filter(user=tutor.user)
        context['form'] = ScheduleForm()
        return context

    def post(self, request, *args, **kwargs):
        tutor = get_object_or_404(Tutor, user=request.user)

        if 'delete_schedule' in request.POST:
            schedule_id = request.POST.get('delete_schedule')
            schedule = get_object_or_404(Schedule, id=schedule_id, user=tutor.user)
            schedule.delete()
            return redirect('update_schedule')

        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = tutor.user
            schedule.save()
            return redirect('update_schedule')

        return self.render_to_response(self.get_context_data(form=form))