import datetime
from django.core.management.base import BaseCommand
from tutorials.models import User, Tutor, Student, Schedule, LessonRequest, AllocatedLesson
from faker import Faker
from random import choice, randint
from datetime import time

# User fixtures
user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe','role': 'admin'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'role': 'tutor'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson', 'role': 'student'},
]


class Command(BaseCommand):
    USER_COUNT = 50
    STUDENT_COUNT = int(USER_COUNT * 0.7)
    TUTOR_COUNT = USER_COUNT - STUDENT_COUNT

    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        print("Seeding users, tutors, and students...")

        self.create_user_fixtures()
        self.create_tutors()
        self.create_students()

        print(f"Seeding complete. {self.TUTOR_COUNT} tutors and {self.STUDENT_COUNT} students created.")

    def create_user_fixtures(self):
        for data in user_fixtures:
            user = create_unique_user(data, self.DEFAULT_PASSWORD)
            if data['role'] == 'tutor':
                Tutor.objects.create(user=user, subjects=choice(Tutor.TOPICS)[0])
            elif data['role'] == 'student':
                Student.objects.create(user=user)
        create_manual_lesson_request()


    def create_tutors(self):
        for i in range(self.TUTOR_COUNT):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            username = create_unique_username(first_name, last_name)
            email = create_unique_email(first_name, last_name)
            user = create_unique_user(
                {'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'role': 'tutor'},
                self.DEFAULT_PASSWORD
            )
            tutor = Tutor.objects.create(
                user=user,
                subjects=choice(Tutor.TOPICS)[0],
            )
            if i % 2 == 0:  # every other tutor gets a pre existing schedule
                self.create_schedule(tutor)

            print(f"\rCreating tutors: {i + 1}/{self.TUTOR_COUNT}", end="")
        print("\nTutors created.")

    def create_students(self):
        tutors = list(Tutor.objects.all())
        if not tutors:
            print("No tutors available for student assignment.")
            return

        for i in range(self.STUDENT_COUNT):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            username = create_unique_username(first_name, last_name)
            email = create_unique_email(first_name, last_name)
            user = create_unique_user(
                {'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'role': 'student'},
                self.DEFAULT_PASSWORD
            )
            tutor = choice(tutors) if randint(1, 100) <= 20 else None  #around 20% pre-assigned students
            Student.objects.create(user=user, tutor=tutor)

            print(f"\rCreating students: {i + 1}/{self.STUDENT_COUNT}", end="")
        print("\nStudents created.")

    def create_schedule(self, tutor):
        num_slots = randint(1, 5)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for _ in range(num_slots):
            day = choice(days)
            start_hour = randint(8, 16)
            end_hour = start_hour + 1
            Schedule.objects.create(
                user=tutor.user,
                day_of_week=day,
                start_time=time(start_hour, 0),
                end_time=time(end_hour, 0),
            )


def create_unique_user(data, password):
    return User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=password,
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data['role']
    )

def create_unique_username(first_name, last_name):
    base_username = f"@{first_name.lower()}{last_name.lower()}"
    counter = 1
    while User.objects.filter(username=base_username).exists():
        base_username = f"@{first_name.lower()}{last_name.lower()}{counter}"
        counter += 1
    return base_username

def create_unique_email(first_name, last_name):
    base_email = f"{first_name.lower()}.{last_name.lower()}@example.org"
    counter = 1
    while User.objects.filter(email=base_email).exists():
        base_email = f"{first_name.lower()}.{last_name.lower()}{counter}@example.org"
        counter += 1
    return base_email


def create_manual_lesson_request():
    # Fetch the student and tutor by username
    student_user = User.objects.get(username='@charlie')
    tutor_user = User.objects.get(username='@janedoe')

    # Create a lesson request
    lesson_request = LessonRequest.objects.create(
        student_id=student_user,
        tutor_id=tutor_user,
        language='Python',
        term='Sept-Dec',
        day_of_the_week='Tuesday',
        frequency='Monthly',
        duration=60,
        description='Manual lesson request for seeding.',
        status='allocated',
        date_created=datetime.datetime(2024, 8, 20)
    )

    # Create the allocated lesson
    lesson_dates = [datetime.datetime(2024, 9, 3), datetime.datetime(2024, 10, 1), datetime.datetime(2024, 11, 5), datetime.datetime(2024, 12, 3)]
    for i in range(len(lesson_dates)):
        AllocatedLesson.objects.create(
            occurrence=i+1,
            date=lesson_dates[i].date(),
            time=lesson_dates[i].time(),
            language=lesson_request.language,
            student_id=lesson_request.student_id,
            tutor_id=lesson_request.tutor_id,
            lesson_request_id=lesson_request.id,
        )