from django.db.models import Q
from rest_framework import permissions, viewsets

from api.permissions import (IsAdminUser, IsManagerOrAdmin,
                             IsTaskAssigneeOrAdmin)
from api.serializers.task import TaskSerializer
from apps.tasks.models import Task


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        """
        Настраиваем права доступа для задач:
        - Список и просмотр: авторизованные пользователи
        - Создание: менеджеры и администраторы
        - Обновление/удаление: администраторы, менеджер проекта или исполнитель
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            permission_classes = [IsManagerOrAdmin]
        else:  # update, partial_update, destroy
            permission_classes = [
                IsTaskAssigneeOrAdmin | IsManagerOrAdmin | IsAdminUser
            ]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Фильтрация задач по ролям:
        - Администраторы видят все задачи
        - Менеджеры видят задачи в своих проектах
        - Сотрудники видят только назначенные им задачи
        """
        user = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()

        if not user.is_authenticated:
            return Task.objects.none()

        if user.is_admin:
            return Task.objects.all()

        if user.is_manager:
            # Менеджеры видят задачи в проектах, где они менеджеры или участники
            return Task.objects.filter(
                Q(project__creator=user) | Q(project__members=user)
            ).distinct()

        # Сотрудники видят только назначенные им задачи
        return Task.objects.filter(assignee=user)
