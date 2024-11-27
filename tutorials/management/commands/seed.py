from django.core.management.base import BaseCommand
from tutorials.models import User, Tutor, Student
from faker import Faker
from random import choice

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'role': 'admin'},
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
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        print("Seeding users, tutors, and students...")

        self.create_user_fixtures()
        self.create_tutors()
        self.create_students()

        print(f"Seeding complete. {self.TUTOR_COUNT} tutors and {self.STUDENT_COUNT} students created.")

    def create_user_fixtures(self):
        for data in user_fixtures:
            self.create_unique_user(data)

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
            Tutor.objects.create(
                user=user,
                subjects=choice(Tutor.TOPICS)[0],
            )
            print(f"\rCreating tutors: {i + 1}", end="")
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
            tutor = choice(tutors)
            Student.objects.create(user=user, tutor=tutor)
            print(f"\rCreating students: {i + 1}", end="")
        print("\nStudents created.")


    def create_unique_user(self, data):
        return User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=self.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role']
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
