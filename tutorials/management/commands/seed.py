from django.core.management.base import BaseCommand
from tutorials.models import User, Tutor, Student
from faker import Faker
from random import choice

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

class Command(BaseCommand):
    USER_COUNT = 300
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
            role = 'tutor' if data['username'] == '@janedoe' else 'student'
            self.create_unique_user(data, role)

    def create_tutors(self):
        for _ in range(self.TUTOR_COUNT):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            username = create_unique_username(first_name, last_name)
            email = create_unique_email(first_name, last_name)
            user = self.create_unique_user(
                {'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name},
                role='tutor'
            )
            Tutor.objects.create(
                user=user,
                expertise=self.faker.job(),
                availability=self.faker.text(max_nb_chars=50)
            )
            print(f"Tutor created: {user.username}")

    def create_students(self):
        tutors = list(Tutor.objects.all())
        if not tutors:
            print("No tutors available for student assignment.")
            return
        for _ in range(self.STUDENT_COUNT):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            username = create_unique_username(first_name, last_name)
            email = create_unique_email(first_name, last_name)
            user = self.create_unique_user(
                {'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name},
                role='student'
            )
            tutor = choice(tutors)
            Student.objects.create(user=user, tutor=tutor)
            print(f"Student created: {user.username}, assigned to tutor: {tutor.user.username}")

    def create_unique_user(self, data, role):
        return User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=self.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role
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
