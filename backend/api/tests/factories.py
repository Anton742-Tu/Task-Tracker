from datetime import date, timedelta

import factory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.files.models import FileAttachment
from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = "employee"


class AdminFactory(UserFactory):
    role = "admin"
    is_staff = True


class ManagerFactory(UserFactory):
    role = "manager"


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"Project {n}")
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
            # Добавляем создателя как члена по умолчанию
            self.members.add(self.creator)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Task {n}")
    description = factory.Faker("paragraph")
    project = factory.SubFactory(ProjectFactory)
    status = "todo"
    priority = "medium"
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))
    creator = factory.SubFactory(ManagerFactory)
    assignee = factory.SubFactory(UserFactory)


class FileAttachmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FileAttachment

    original_filename = factory.Sequence(lambda n: f"file{n}.jpg")
    file_type = "image"
    mime_type = "image/jpeg"
    file_size = 1024  # 1KB
    uploaded_by = factory.SubFactory(UserFactory)
    description = factory.Faker("sentence")
    is_public = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Создаем временный файл"""
        file = SimpleUploadedFile(
            name=kwargs.get("original_filename", "test.jpg"),
            content=b"test content",
            content_type="image/jpeg",
        )
        kwargs["file"] = file
        return super()._create(model_class, *args, **kwargs)
