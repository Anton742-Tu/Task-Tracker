from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from api.serializers.project import ProjectSerializer
from apps.projects.models import Project


class ProjectViewSet(viewsets.ModelViewSet):
    # Добавляем обязательные атрибуты
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["name", "description"]
