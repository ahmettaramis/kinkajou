# Generated by Django 5.1.2 on 2024-12-11 14:28

import django.contrib.auth.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(message='Username must consist of @ followed by at least three alphanumericals', regex='^@\\w{3,}$')])),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('tutor', 'Tutor'), ('student', 'Student')], default='student', max_length=10, verbose_name='Role')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='LessonRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('Python', 'Python'), ('Java', 'Java'), ('C++', 'C++'), ('Scala', 'Scala'), ('R', 'R'), ('Javascript', 'Javascript'), ('Swift', 'Swift'), ('Go', 'Go')], max_length=50)),
                ('term', models.CharField(choices=[('Sept-Christmas', 'Sept-Christmas'), ('Jan-Easter', 'Jan-Easter'), ('March-June', 'March-June')], max_length=20)),
                ('day_of_the_week', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=10)),
                ('frequency', models.CharField(choices=[('Weekly', 'Weekly'), ('Bi-Weekly', 'Bi-Weekly'), ('Monthly', 'Monthly')], max_length=10)),
                ('duration', models.IntegerField(choices=[(60, '60 minutes'), (120, '120 minutes')])),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_requests_as_student', to=settings.AUTH_USER_MODEL)),
                ('tutor_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lesson_requests_as_tutor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subjects', models.CharField(blank=True, choices=[('Python', 'Python'), ('Java', 'Java'), ('C++', 'C++'), ('Scala', 'Scala'), ('R', 'R'), ('Javascript', 'Javascript'), ('Swift', 'Swift'), ('Go', 'Go')], max_length=50, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tutor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
                ('tutor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='tutorials.tutor')),
            ],
        ),
        migrations.CreateModel(
            name='AllocatedLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('occurrence', models.PositiveIntegerField()),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('language', models.CharField(max_length=100)),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allocated_lessons_as_student', to=settings.AUTH_USER_MODEL)),
                ('tutor_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='allocated_lessons_as_tutor', to=settings.AUTH_USER_MODEL)),
                ('lesson_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allocated_lessons', to='tutorials.lessonrequest')),
            ],
            options={
                'unique_together': {('lesson_request', 'occurrence')},
            },
        ),
    ]
