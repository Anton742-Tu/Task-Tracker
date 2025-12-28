from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.project import ProjectViewSet
from api.views.task import TaskViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
]
