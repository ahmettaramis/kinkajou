from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from .forms import LessonRequestForm
from .models import Invoice, Lesson, LessonRequest
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.admin.views.decorators import staff_member_required


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

@login_required
def role_based_redirect(request):
    user_profile = request.user.profile
    if user_profile.role == 'admin':
        return redirect('admin_dashboard')
    elif user_profile.role == 'tutor':
        return redirect('tutor_dashboard')
    elif user_profile.role == 'student':
        return redirect('student_dashboard')
    return redirect('dashboard')

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def tutor_dashboard(request):
    return render(request, 'tutor_dashboard.html')

@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html')

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

class CustomLoginView(LoginView):
    def form_valid(self, form):
        # Log in the user
        login(self.request, form.get_user())
        user_profile = self.request.user.profile
        if user_profile.role == 'admin':
            return redirect('admin_dashboard')
        elif user_profile.role == 'tutor':
            return redirect('tutor_dashboard')
        elif user_profile.role == 'student':
            return redirect('student_dashboard')
        return super().form_valid(form)

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

def request_lesson(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            lesson_request = form.save(commit=False)
            lesson_request.student = request.user
            lesson_request.status = 'pending'
            lesson_request.save()
            # Send email or notification here
            return redirect('lesson_request_success')
    else:
        form = LessonRequestForm()
    return render(request, 'request_lesson.html', {'form': form})

def schedule_lesson(request, lesson_id):
    # Get lesson request, display tutor availability, and allow admins to schedule
    pass


def generate_invoice(lesson):
    # Code to create an invoice for a lesson
    pass

def view_invoices(request):
    invoices = Invoice.objects.filter(student=request.user)
    return render(request, 'invoices.html', {'invoices': invoices})

def student_schedule(request):
    lessons = Lesson.objects.filter(request__student=request.user)
    return render(request, 'student_schedule.html', {'lessons': lessons})

def tutor_schedule(request):
    lessons = Lesson.objects.filter(tutor=request.user)
    return render(request, 'tutor_schedule.html', {'lessons': lessons})

@staff_member_required
def assign_tutor(request, lesson_id):
    lesson_request = get_object_or_404(LessonRequest, id=lesson_id)
    # Logic to assign a tutor and mark request as approved
    return redirect('admin_dashboard')