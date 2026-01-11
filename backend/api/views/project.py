from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from api.permissions import IsAdminUser, IsManagerOrAdmin, IsProjectMemberOrAdmin
from api.serializers.project import ProjectSerializer
from apps.projects.models import Project


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["name", "description"]

    def get_permissions(self):
        """
        Настраиваем права доступа:
        - Список и просмотр: любой авторизованный пользователь
        - Создание: менеджеры и администраторы
        - Обновление/удаление: администраторы или создатель проекта
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            permission_classes = [IsManagerOrAdmin]
        else:  # update, partial_update, destroy
            permission_classes = [IsProjectMemberOrAdmin | IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Фильтрация проектов по ролям:
        - Администраторы видят все
        - Менеджеры видят свои проекты и проекты, где они участники
        - Сотрудники видят только проекты, где они участники
        """
        user = self.request.user

        # Для генерации схемы Swagger
        if getattr(self, "swagger_fake_view", False):
            return Project.objects.none()

        if not user.is_authenticated:
            return Project.objects.none()

        if user.is_admin:
            return Project.objects.all()

        # Базовый запрос: проекты где пользователь создатель или участник
        queryset = Project.objects.filter(Q(creator=user) | Q(members=user)).distinct()

        return queryset

    def perform_create(self, serializer):
        """Автоматически назначаем создателя проекта"""
        serializer.save(creator=self.request.user)
