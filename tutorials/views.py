from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from .models import LessonRequest
from .forms import LessonRequestForm
from .models import LessonSchedule
from django.core.exceptions import PermissionDenied
from datetime import datetime


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})


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

# Check if user is a student
def is_student(user):
    return not user.is_staff

# Check if user is an admin
def is_admin(user):
    return user.is_staff

# Student: Submit Lesson Request
@login_required
@user_passes_test(is_student)
def create_lesson_request(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            lesson_request = form.save(commit=False)
            lesson_request.student = request.user  #Link to the logged-in student
            lesson_request.save()
            return redirect('student_requests')
    else:
        form = LessonRequestForm()
    return render(request, 'lesson_requests/create_request.html', {'form': form})

# Student: View Own Requests
@login_required
@user_passes_test(is_student)
def student_view_requests(request):
    requests = LessonRequest.objects.filter(student=request.user)
    return render(request, 'lesson_requests/student_view_requests.html', {'requests': requests})

# Admin: View All Requests
@login_required
@user_passes_test(is_admin)
def admin_view_requests(request):
    status_filter = request.GET.get('status')  # Get status filter from query params
    if status_filter:
        requests = LessonRequest.objects.filter(status=status_filter)
    else:
        requests = LessonRequest.objects.all()
    return render(request, 'lesson_requests/admin_view_requests.html', {'requests': requests})

# Admin: Update Request Status
@login_required
@user_passes_test(is_admin)
def update_request_status(request, pk):
    lesson_request = get_object_or_404(LessonRequest, pk=pk)

    # Get the existing LessonSchedule if the lesson is already allocated
    lesson_schedule = LessonSchedule.objects.filter(
        student=lesson_request.student,
        tutor=lesson_request.preferred_tutor,
        lesson_date=lesson_request.lesson_date
    ).first()

    if request.method == 'POST':
        # Get updated values from the form
        new_status = request.POST.get('status')
        venue = request.POST.get('venue', 'Online')
        time_str = request.POST.get('time')

        # Convert the date and time string to a datetime object if provided
        lesson_date = None
        if time_str:
            try:
                lesson_date = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                messages.error(request, "Invalid time format.")
                return render(request, 'lesson_requests/update_request_status.html', {'lesson_request': lesson_request})

        if new_status == 'allocated':
            # If no tutor is assigned, show an error
            tutor = lesson_request.preferred_tutor
            if not tutor:
                messages.error(request, "Please assign a preferred tutor before allocating.")
                return render(request, 'lesson_requests/update_request_status.html', {'lesson_request': lesson_request})

            # Update or create the LessonSchedule
            if lesson_schedule:
                # Update existing schedule
                lesson_schedule.lesson_date = lesson_date if lesson_date else lesson_schedule.lesson_date
                lesson_schedule.venue = venue
                lesson_schedule.save()

                # Update lesson request with new date
                lesson_request.lesson_date = lesson_date if lesson_date else lesson_request.lesson_date
                lesson_request.status = new_status
                lesson_request.save()
            else:
                # Create a new schedule if not allocated before
                LessonSchedule.objects.create(
                    student=lesson_request.student,
                    tutor=tutor,
                    lesson_date=lesson_date,
                    venue=venue,
                )
                lesson_request.status = new_status
                lesson_request.lesson_date = lesson_date
                lesson_request.save()

            messages.success(request, "Lesson request has been successfully allocated and scheduled.")
        else:
            # Update the lesson request to 'unallocated' and remove its schedule
            if lesson_schedule:
                lesson_schedule.delete()

            lesson_request.status = new_status
            lesson_request.lesson_date = None
            lesson_request.save()
            messages.success(request, "Lesson request status updated successfully.")

        return redirect('admin_view_requests')

    return render(request, 'lesson_requests/update_request_status.html', {
        'lesson_request': lesson_request,
        'lesson_schedule': lesson_schedule,
    })