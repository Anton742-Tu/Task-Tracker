from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from api.serializers.project import ProjectSerializer
from apps.projects.models import Project, models


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["name", "description"]

    def get_permissions(self):
        """
        Разные права для разных действий
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Пользователи видят только свои проекты или проекты, где они участники
        """
        user = self.request.user

        # Для генерации схемы Swagger
        if getattr(self, "swagger_fake_view", False):
            return Project.objects.none()

        if user.is_superuser:
            return Project.objects.all()

        # Обычные пользователи видят проекты, где они создатель или участник
        return Project.objects.filter(
            models.Q(creator=user) | models.Q(members=user)
        ).distinct()
