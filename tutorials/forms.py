"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import User, Invoice, LessonRequest
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from .models import User, Schedule

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            role=self.cleaned_data.get('role'),
            password=self.cleaned_data.get('new_password'),
        )
        return user

User = get_user_model()


class LessonRequestForm(forms.ModelForm):
    class Meta:
        model = LessonRequest
        fields = [
            'language', 'term', 'day_of_the_week', 'frequency',
            'duration', 'description', 'tutor_id'
        ]
        widgets = {
            'language': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'day_of_the_week': forms.Select(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Provide additional details (optional)',
                'maxlength': '1000',
            }),
            'tutor_id': forms.Select(
                attrs={'class': 'form-control', 'placeholder': 'Select a preferred tutor (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter tutors for the dropdown
        self.fields['tutor_id'].queryset = User.objects.filter(role="tutor")
        self.fields['description'].required = False  # Optional
        self.fields['tutor_id'].required = False  # Optional

    def clean_tutor_id(self):
        tutor = self.cleaned_data.get('tutor_id')
        if tutor and tutor.role != "tutor":
            raise ValidationError("Selected user is not a tutor.")
        return tutor

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) > 1000:
            raise forms.ValidationError("Description cannot exceed 1000 characters.")
        return description
    
    def clean_no_of_weeks(self):
        no_of_weeks = self.cleaned_data.get('no_of_weeks')
        if no_of_weeks is None or not (1 <= no_of_weeks <= 52):
            raise forms.ValidationError("Number of weeks must be between 1 and 52.")
        return no_of_weeks
    

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.Select(choices=[(f"{h}:00", f"{h}:00") for h in range(8, 20)], attrs={'class': 'form-control'}),
            'end_time': forms.Select(choices=[(f"{h}:00", f"{h}:00") for h in range(9, 21)], attrs={'class': 'form-control'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            self.add_error('start_time', 'Start Time cannot be before End Time')

        return cleaned_data

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['lesson_request', 'is_paid', 'amount']
        widgets = {
            'lesson_request': forms.HiddenInput(),
            'is_paid': forms.CheckboxInput(),
        }