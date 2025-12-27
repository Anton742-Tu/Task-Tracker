from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from api.permissions.permissions import (IsProjectMember,
                                         IsTaskAssigneeOrCreator)
from api.serializers.task import TaskSerializer
from apps.tasks.models import Task


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с задачами."""

    serializer_class = TaskSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["project", "status", "priority", "assignee"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority"]
    ordering = ["-priority", "-created_at"]

    def get_queryset(self):
        """Возвращает задачи доступные пользователю."""
        user = self.request.user

        # Для администраторов - все задачи
        if user.is_staff:
            return Task.objects.all()

        # Для обычных пользователей - задачи в их проектах
        return Task.objects.filter(project__members=user).distinct()

    def get_permissions(self):
        """Настройка прав доступа в зависимости от действия."""
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated, IsProjectMember]
        elif self.action in ["create"]:
            permission_classes = [permissions.IsAuthenticated]
        else:  # update, partial_update, destroy
            permission_classes = [permissions.IsAuthenticated, IsTaskAssigneeOrCreator]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Дополнительная логика при создании задачи."""
        # Проверяем что пользователь является участником проекта
        project = serializer.validated_data.get("project")
        if project and not project.members.filter(id=self.request.user.id).exists():
            raise serializers.ValidationError(
                {"project": "Вы не являетесь участником этого проекта"}
            )

        serializer.save()
