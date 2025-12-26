from rest_framework import serializers

from apps.projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Project."""

    creator_name = serializers.CharField(source="creator.get_full_name", read_only=True)
    task_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "status",
            "creator",
            "creator_name",
            "members",
            "created_at",
            "updated_at",
            "task_count",
        ]
        read_only_fields = ["id", "creator", "created_at", "updated_at", "task_count"]

    def create(self, validated_data):
        """Создание проекта с текущим пользователем в качестве создателя."""
        request = self.context.get("request")
        validated_data["creator"] = request.user
        return super().create(validated_data)
