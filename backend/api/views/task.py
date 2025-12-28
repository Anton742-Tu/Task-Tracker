from rest_framework import viewsets

from api.serializers.task import TaskSerializer
from apps.tasks.models import Task


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
