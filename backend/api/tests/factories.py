import random
import string

import factory
from django.contrib.auth import get_user_model

from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


def random_string(length=8):
    """Генерация случайной строки"""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyFunction(lambda: f"user_{random_string()}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = "employee"


class ManagerFactory(UserFactory):
    role = "manager"


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.LazyFunction(lambda: f"Project_{random_string()}")
    description = factory.Faker("paragraph")
    status = "active"
    creator = factory.SubFactory(ManagerFactory)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in extracted:
                self.members.add(member)
        else:
            self.members.add(self.creator)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.LazyFunction(lambda: f"Task_{random_string()}")
    description = factory.Faker("paragraph")
    project = factory.SubFactory(ProjectFactory)
    status = "todo"
    priority = "medium"
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))
    creator = factory.SubFactory(ManagerFactory)
    assignee = factory.SubFactory(UserFactory)
