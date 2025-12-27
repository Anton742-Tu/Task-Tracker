from rest_framework import serializers

from apps.tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Task."""

    # project_info = ProjectSerializer(source="project", read_only=True)
    assignee_name = serializers.CharField(
        source="assignee.get_full_name", read_only=True, allow_null=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "project",
            "project_info",
            "assignee",
            "assignee_name",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        """Валидация данных задачи."""
        # Проверка что срок выполнения не в прошлом
        due_date = data.get("due_date")
        if due_date:
            from django.utils import timezone

            if due_date < timezone.now().date():
                raise serializers.ValidationError(
                    {"due_date": "Срок выполнения не может быть в прошлом"}
                )

        # Проверка что исполнитель является участником проекта
        project = (
            data.get("project") or self.instance.project if self.instance else None
        )
        assignee = data.get("assignee")

        if project and assignee:
            if not project.members.filter(id=assignee.id).exists():
                raise serializers.ValidationError(
                    {"assignee": "Исполнитель должен быть участником проекта"}
                )

        return data

    def create(self, validated_data):
        """Создание задачи с валидацией."""
        request = self.context.get("request")

        # Если создатель не указан, назначаем текущего пользователя
        if "assignee" not in validated_data and request:
            validated_data["assignee"] = request.user

        return super().create(validated_data)
