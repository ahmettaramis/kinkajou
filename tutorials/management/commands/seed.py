from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import Group
from tutorials.models import User, Lesson, Invoice

import pytz
from faker import Faker
from datetime import timezone
from random import randint, random, choice

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'is_staff' : True, 'groups': ['Admins', 'Students', 'Tutors']},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'is_staff' : False, 'groups': ['Tutors']},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson', 'is_staff' : False, 'groups': ['Students']},
]
seed_groups = ['Students', 'Tutors']


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 100
    LESSON_COUNT = 50
    INVOICE_COUNT = 21
    DEFAULT_PASSWORD = 'Password123'
    user_groups = ['Admins', 'Students', 'Tutors']
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_user_groups()
        self.groups = Group.objects.all()
    
        self.create_users()
        self.users = User.objects.all()

        self.create_lessons()
        self.lessons = Lesson.objects.all()

        self.create_invoices()
        self.invoices = Invoice.objects.all()
    
    def create_user_groups(self):
        for group_name in self.user_groups:
            group, _ = Group.objects.get_or_create(name=group_name)
        
        print("User group seeding complete.     ")

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def create_lessons(self):
        lesson_count = Lesson.objects.count()
        while  lesson_count < self.LESSON_COUNT:
            self.generate_lesson()
            lesson_count = Lesson.objects.count()
        print("Lesson seeding complete.     ")

    def generate_lesson(self):
        tutor = choice(User.objects.filter(groups__name='Tutors'))
        student = choice(User.objects.filter(groups__name='Students'))
        description = "Seeded description."
        time = self.faker.date_time(tzinfo=timezone.utc)

        Lesson.objects.create(
            tutor=tutor,
            student=student,
            description=description,
            time=time
        )

    def create_invoices(self):
        invoice_count = Invoice.objects.count()
        while  invoice_count < self.INVOICE_COUNT:
            self.generate_invoice()
            invoice_count = Invoice.objects.count()
        print("Invoice seeding complete.     ")

    def generate_invoice(self):
        lesson = choice(Lesson.objects.all())
        amount = randint(10,100)
        is_paid = False
        created_at = self.faker.date_time(tzinfo=timezone.utc)

        Invoice.objects.create(
            lesson=lesson,
            amount=amount,
            is_paid=is_paid,
            created_at=created_at
        )

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        is_staff = False
        groups = [choice(seed_groups)]
        self.try_create_user(
            {'username': username, 
            'email': email, 
            'first_name': first_name, 
            'last_name': last_name, 
            'is_staff' : is_staff,
            'groups' : groups}
            )
       
    def try_create_user(self, data):
        try:
            self.create_user(data)
        except Exception as e:
            print(f"Error creating user: {e}")

    def create_user(self, data):
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_staff=data['is_staff']
        )

        # Assign groups after the user is created
        for group_name in data['groups']:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        user.save()

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'
