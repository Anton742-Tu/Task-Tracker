from rest_framework import permissions, viewsets

from api.serializers.project import ProjectSerializer
from apps.projects.models import Project


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с проектами."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает только проекты, где пользователь является участником."""
        user = self.request.user
        return Project.objects.filter(members=user).distinct()

    def perform_create(self, serializer):
        """Сохраняет проект с текущим пользователем в качестве создателя и участника."""
        project = serializer.save()
        project.members.add(self.request.user)
