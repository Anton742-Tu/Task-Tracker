from rest_framework import Project, ProjectSerializer, permissions, viewsets


class IsProjectMember(permissions.BasePermission):
    """Базовая проверка - пользователь участник проекта."""

    def has_object_permission(self, request, view, obj):
        # Пока просто возвращаем True для теста
        return True


class IsAuthenticatedReadOnly(permissions.BasePermission):
    """Только чтение для аутентифицированных."""

    def has_permission(self, request, view):
        return request.method in ["GET", "HEAD", "OPTIONS"]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedReadOnly]  # ← Пока только чтение
