from rest_framework import serializers

from apps.projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Минимальный сериализатор для теста."""

    class Meta:
        model = Project
        fields = ["id", "name", "description", "creator", "members"]
        read_only_fields = ["id", "creator"]
