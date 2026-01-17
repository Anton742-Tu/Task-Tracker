import filetype
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from apps.files.models import FileAttachment
from apps.projects.models import Project
from apps.tasks.models import Task


class FileAttachmentSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о файле"""

    file_size_human = serializers.CharField(read_only=True)
    extension = serializers.CharField(read_only=True)
    uploaded_by_username = serializers.CharField(
        source="uploaded_by.username", read_only=True
    )
    is_image = serializers.SerializerMethodField()
    is_document = serializers.SerializerMethodField()

    class Meta:
        model = FileAttachment
        fields = [
            "id",
            "file",
            "original_filename",
            "file_type",
            "mime_type",
            "file_size",
            "file_size_human",
            "extension",
            "task",
            "project",
            "user",
            "uploaded_by",
            "uploaded_by_username",
            "description",
            "upload_date",
            "is_public",
            "is_image",
            "is_document",
        ]
        read_only_fields = [
            "id",
            "original_filename",
            "file_type",
            "mime_type",
            "file_size",
            "uploaded_by",
            "upload_date",
            "is_image",
            "is_document",
        ]

    def get_is_image(self, obj):
        """Проверяет, является ли файл изображением"""
        return obj.file_type == "image"

    def get_is_document(self, obj):
        """Проверяет, является ли файл документом"""
        return obj.file_type == "document"

    def to_representation(self, instance):
        """Добавляем URL файла в ответ"""
        representation = super().to_representation(instance)

        # Добавляем URL файла
        if instance.file:
            request = self.context.get("request")
            if request:
                representation["file_url"] = request.build_absolute_uri(
                    instance.file.url
                )
            else:
                representation["file_url"] = instance.file.url

        return representation


class FileUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки файлов"""

    file = serializers.FileField(required=True, help_text="Загружаемый файл")

    task_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID задачи, к которой прикрепляется файл",
    )

    project_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID проекта, к которому прикрепляется файл",
    )

    description = serializers.CharField(
        required=False, allow_blank=True, max_length=500, help_text="Описание файла"
    )

    is_public = serializers.BooleanField(
        required=False, default=False, help_text="Публичный ли доступ к файлу"
    )

    def validate_file(self, value):
        """Валидация файла"""
        if not isinstance(value, UploadedFile):
            raise serializers.ValidationError("Некорректный файл")

        # Проверяем размер файла
        if value.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"Файл слишком большой. Максимальный размер: {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
            )

        # Определяем MIME тип с помощью filetype
        try:
            # Читаем начало файла для определения типа
            file_content = value.read(2048)  # ← ПЕРВОЕ: читаем файл
            value.seek(0)  # Возвращаем указатель на начало

            # Используем filetype для определения MIME типа
            kind = filetype.guess(file_content)  # ← ВТОРОЕ: определяем тип
            if kind:
                mime_type = kind.mime
            else:
                # Если filetype не смог определить
                mime_type = value.content_type or "application/octet-stream"
        except Exception as e:
            # Если ошибка, используем content_type из файла
            print(f"Error determining file type: {e}")
            mime_type = value.content_type or "application/octet-stream"

        # Проверяем разрешенные типы
        if mime_type not in settings.ALLOWED_FILE_TYPES:
            raise serializers.ValidationError(
                f"Тип файла {mime_type} не поддерживается. "
                f"Разрешенные типы: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )

        return value

    def validate(self, data):
        """Валидация данных"""
        # Проверяем, что файл прикреплен либо к задаче, либо к проекту, либо к пользователю
        task_id = data.get("task_id")
        project_id = data.get("project_id")

        if not task_id and not project_id:
            # Если не прикреплено ни к чему, прикрепляем к текущему пользователю
            request = self.context.get("request")
            if request and request.user:
                pass  # ОК, прикрепится к пользователю
            else:
                raise serializers.ValidationError(
                    "Файл должен быть прикреплен к задаче, проекту или пользователю"
                )

        # Проверяем существование задачи
        if task_id:
            try:
                task = Task.objects.get(id=task_id)
                data["task"] = task
            except Task.DoesNotExist:
                raise serializers.ValidationError({"task_id": "Задача не найдена"})

        # Проверяем существование проекта
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                data["project"] = project
            except Project.DoesNotExist:
                raise serializers.ValidationError({"project_id": "Проект не найдена"})

        return data

    def create(self, validated_data):
        """Создание записи о файле"""
        request = self.context.get("request")

        # Извлекаем данные
        file_obj = validated_data.pop("file")
        task = validated_data.pop("task", None)
        project = validated_data.pop("project", None)
        description = validated_data.get("description", "")
        is_public = validated_data.get("is_public", False)

        # Создаем запись файла
        file_attachment = FileAttachment(
            file=file_obj,
            task=task,
            project=project,
            user=request.user if request else None,
            uploaded_by=request.user if request else None,
            description=description,
            is_public=is_public,
        )

        file_attachment.save()
        return file_attachment


class FileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления файла (только метаданные)"""

    class Meta:
        model = FileAttachment
        fields = ["description", "is_public"]
