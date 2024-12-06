"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import User, LessonRequest
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
        fields = ['title', 'description', 'lesson_date', 'preferred_tutor', 'no_of_weeks']
        widgets = {
            'lesson_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a title of your lesson'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Provide a description for your lesson request', 'maxlength': '1000'}),
            'preferred_tutor': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select a preferred tutor (optional)'}),
            'no_of_weeks': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter how many weeks you want this lesson (1-52)', 'min': 1, 'max': 52}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter tutors for the dropdown
        self.fields['preferred_tutor'].queryset = User.objects.filter(role = "tutor")

        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['lesson_date'].required = True
        self.fields['preferred_tutor'].required = False
        self.fields['no_of_weeks'].required = True
    
    def clean_lesson_date(self):
        # Validate lesson_date is not in the past
        lesson_date = self.cleaned_data.get('lesson_date')
        if lesson_date and lesson_date < now():
            raise ValidationError("Lesson date cannot be in the past.")
        return lesson_date

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) > 1000:
            raise forms.ValidationError("Description cannot exceed 1000 characters.")
        return description

    

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
