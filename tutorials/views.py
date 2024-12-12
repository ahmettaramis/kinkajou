from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render, get_object_or_404, get_object_or_404, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.db.models import Prefetch
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, InvoiceForm
from tutorials.helpers import login_prohibited
from tutorials.models import Invoice
from .models import User, Tutor, Schedule
from .forms import ScheduleForm
from .models import LessonRequest, AllocatedLesson
from .forms import LessonRequestForm
from .helpers import *


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user

    if current_user.role == 'student':
        # Fetch lessons allocated to the current student
        allocated_lessons = AllocatedLesson.objects.filter(student_id=current_user)
        invoices = Invoice.objects.filter(lesson_request_id__student_id=current_user)

        # Count unpaid invoices
        invoice_actions_needed = invoices.filter(is_paid=False).count()

        context = {
            'user': current_user,
            'allocated_lessons': allocated_lessons,
            'invoice_actions_needed': invoice_actions_needed
        }

    elif current_user.role == 'tutor':
        # Fetch lessons allocated to the current tutor
        allocated_lessons = AllocatedLesson.objects.filter(tutor_id=current_user)

        # Tutors don't need invoice_actions_needed logic
        context = {
            'user': current_user,
            'allocated_lessons': allocated_lessons
        }

    else:
        # If the user is an admin or another role
        # Show all allocated lessons or apply custom logic
        allocated_lessons = AllocatedLesson.objects.all()

        # Admins or other roles don't need invoice_actions_needed logic
        context = {
            'user': current_user,
            'allocated_lessons': allocated_lessons
        }

    return render(request, 'dashboard.html', context)


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
            lesson_request.student_id = request.user
            lesson_request.save()
            return redirect('student_view_requests')
    else:
        form = LessonRequestForm()
    return render(request, 'lesson_requests/create_request.html', {'form': form})


# Student: View Own Requests
@login_required
@is_student
def student_view_requests(request):
    requests = LessonRequest.objects.filter(student_id=request.user)
    return render(request, 'lesson_requests/student_view_requests.html', {'requests': requests})


# Student: View own invoices
@login_required
@is_student
def student_view_invoices(request):
    invoices = Invoice.objects.filter(lesson_request_id__student_id=request.user)
    return render(request, 'student_view_invoices.html', {'invoices': invoices})


# Admin: View All Submitted Requests
@login_required
@is_admin
def admin_view_requests(request):
    filter = request.GET.get('filter') or ""
    invoices = Invoice.objects.all()
    requests = []
    if filter in ["allocated", "unallocated"]:
        requests = LessonRequest.objects.filter(status=filter)
    elif filter == "paid":
        requests = LessonRequest.objects.filter(invoice__is_paid=True)
    elif filter == "unpaid":
        requests = LessonRequest.objects.filter(invoice__is_paid=False)
    elif filter == "invoice_generated":
        requests = LessonRequest.objects.filter(invoice__isnull=False)
    elif filter == "no_invoice_generated":
        requests = LessonRequest.objects.filter(invoice__isnull=True)
    else:
        requests = LessonRequest.objects.all()

    return render(request, 'lesson_requests/admin_view_requests.html', {'requests': requests, 'invoices': invoices, 'filter': filter})


# Admin: Update Request Status
@login_required
@is_admin
def update_request_status(request, pk):
    lesson_request = get_object_or_404(LessonRequest, pk=pk)
    tutors = User.objects.filter(role = "tutor")

    if request.method == 'POST':
        new_status = request.POST.get('status')
        selected_tutor_id = request.POST.get('lesson_requests_as_tutor')
        start_time_str = request.POST.get('start_time')

        # Validate that a tutor is selected if allocating
        if new_status == 'allocated' and not selected_tutor_id:
            messages.error(request, "You must assign a tutor before allocating the lesson.")
        elif new_status == 'allocated' and not start_time_str:
            messages.error(request, "You must provide a start time before allocating the lesson.")
        else:
            # If status is changing from allocated to unallocated delete allocated lessons
            if lesson_request.status == 'allocated' and new_status == 'unallocated':
                AllocatedLesson.objects.filter(lesson_request_id=lesson_request).delete()
                messages.success(request, "Allocated lessons have been deleted.")

            # Assign the tutor if provided
            if selected_tutor_id:
                tutor = User.objects.get(id=selected_tutor_id)
                lesson_request.tutor_id = tutor 
                messages.success(request, f"Tutor {tutor.username} assigned successfully.")

            # Update the status
            lesson_request.status = new_status
            lesson_request.save()

            # Create allocated lessons if status is allocated
            if new_status == 'allocated':
                AllocatedLesson.objects.filter(lesson_request=lesson_request).delete()
                term_start_date, term_end_date = get_term_date_range(lesson_request.term, lesson_request.date_created)

                # Calculate lesson frequency
                frequency_mapping = {
                    'Weekly': timedelta(weeks=1),
                    'Bi-Weekly': timedelta(weeks=2),
                    'Monthly': timedelta(weeks=4),
                }
                delta = frequency_mapping.get(lesson_request.frequency)

                if not delta:
                    messages.error(request, "Invalid frequency specified for the lesson request.")
                    return redirect('admin_view_requests')
                
                # Loop to create lessons within the term date range
                lesson_date = term_start_date
                occurrence = 1

                while lesson_date <= term_end_date:
                    # Adjust lesson_date to match the day_of_the_week
                    while lesson_date.weekday() != day_to_num(lesson_request.day_of_the_week):
                        lesson_date += timedelta(days=1)

                    if lesson_date > term_end_date:
                        break
                
                # Create an AllocatedLesson instance
                    AllocatedLesson.objects.create(
                        lesson_request=lesson_request,
                        occurrence=occurrence,
                        date=lesson_date,
                        time=datetime.strptime(request.POST.get('start_time'), '%H:%M').time(),
                        language=lesson_request.language,
                        student_id=lesson_request.student_id,
                        tutor_id=lesson_request.tutor_id,
                    )
                    occurrence += 1
                    lesson_date += delta

            # Redirect with a success message
            messages.success(request, f"Lesson request status updated to '{new_status}'.")
            return redirect('admin_view_requests')

    return render(request, 'lesson_requests/update_request_status.html', {
        'lesson_request': lesson_request,
        'tutors': tutors
    })


def day_to_num(day):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days.index(day)


def get_term_date_range(term, date_created):
    if not isinstance(date_created, datetime):
        raise TypeError("date_created must be a datetime object")

    current_year = date_created.year
    if term == 'Sept-Christmas':
        lower_date = datetime(current_year, 9, 1)
        upper_date = datetime(current_year, 12, 25)
    elif term == 'Jan-Easter':
        lower_date = datetime(current_year, 1, 1)
        upper_date = datetime(current_year, 4, 15)
    elif term == 'March-June':
        lower_date = datetime(current_year, 3, 1)
        upper_date = datetime(current_year, 6, 30)
    else:
        raise ValueError(f"Unknown term: {term}")

    # Ensure both are offset-naive
    if date_created.tzinfo is not None:
        date_created = date_created.replace(tzinfo=None)  # Remove timezone info

    if upper_date.tzinfo is not None:
        upper_date = upper_date.replace(tzinfo=None)  # Remove timezone info

    # If the term has already passed this year, set it for next year
    if date_created > upper_date:
        lower_date = lower_date.replace(year=current_year + 1)
        upper_date = upper_date.replace(year=current_year + 1)

    return lower_date, upper_date


@login_required
def cancel_lesson(request, lesson_id):
    if request.method == 'POST':
        # Get the lesson and ensure the current user is either the student or the tutor for the lesson
        lesson = get_object_or_404(AllocatedLesson, id=lesson_id)
        
        # Check if the current user is either the student or the tutor for this lesson
        if lesson.lesson_request.student_id == request.user or lesson.tutor_id == request.user:
            lesson.delete()
            messages.success(request, "Lesson has been cancelled successfully.")
        else:
            messages.error(request, "You do not have permission to cancel this lesson.")

        return redirect('dashboard')

    # Return 405 for methods other than POST
    return HttpResponseNotAllowed(['POST'])


class TutorListView(ListView):
    """View to display all tutors."""
    
    model = Tutor
    template_name = 'tutor_list.html'
    context_object_name = 'tutors'

    day_order = {
        "Monday": 2, "Tuesday": 3, "Wednesday": 4, "Thursday": 5,
        "Friday": 6, "Saturday": 7, "Sunday": 1,
    }

    def dispatch(self, request, *args, **kwargs):
        # Redirect to home if the user is not an admin
        if request.user.role != 'admin':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

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
        """Provide context for populating dropdowns and availability."""
        context = super().get_context_data(**kwargs)
        context['subjects'] = Tutor.TOPICS  # Pass subjects to the template
        context['days'] = Schedule.DAYS_OF_WEEK  # Pass days to the template

        # Add availability with sorting
        tutors = context['tutors']
        for tutor in tutors:
            schedules = Schedule.objects.filter(user=tutor.user)
            sorted_schedules = sorted(
                schedules,
                key=lambda s: (self.day_order.get(s.day_of_week, 8), s.start_time)
            )
            tutor.availability = sorted_schedules  # Attach sorted schedules to the tutor

        context['form'] = ScheduleForm  # Add the Schedule form to the context
        return context



class TutorAvailabilityUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'update_schedule.html'

    def dispatch(self, request, *args, **kwargs):
        # Redirect to home if the user is not a tutor
        if request.user.role != 'tutor':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tutor = get_object_or_404(Tutor, user=self.request.user)

        # Define the day order mapping
        day_order = {
            "Monday": 2, "Tuesday": 3, "Wednesday": 4, "Thursday": 5,
            "Friday": 6, "Saturday": 7, "Sunday": 1,
        }

        # Fetch schedules and sort them by day_of_week and start_time
        schedules = Schedule.objects.filter(user=tutor.user)
        sorted_schedules = sorted(
            schedules,
            key=lambda s: (day_order.get(s.day_of_week, 8), s.start_time)
        )
        context['availability'] = sorted_schedules
        context['form'] = ScheduleForm
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


@login_required
@is_admin
def toggle_invoice_paid(request, invoice_id):
    if request.method == 'GET':
        invoice = get_object_or_404(Invoice, id=invoice_id)
        invoice.is_paid = not invoice.is_paid
        invoice.save()
        return redirect('admin_view_requests')
    
    return HttpResponseNotAllowed(['GET'])


@login_required
@is_admin
def generate_invoice(request, lesson_request_id):
    lesson_request = get_object_or_404(LessonRequest, id=lesson_request_id)
    try:
        invoice = Invoice.objects.get(lesson_request=lesson_request)
    except Invoice.DoesNotExist:
        invoice = None

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if invoice:
            invoice.delete()

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.lesson_request = lesson_request 
            invoice.save()
            return redirect('admin_view_requests') 
    else:
        form = InvoiceForm(initial={'lesson_request': lesson_request, 'is_paid': False})
    
    return render(request, 'generate_invoice.html', {'form': form, 'lesson_request': lesson_request, 'invoice': invoice})
