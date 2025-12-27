from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from api.views.project import ProjectViewSet
from api.views.task import TaskViewSet

# Основной router
router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")

# Nested router для задач
projects_router = routers.NestedSimpleRouter(router, r"projects", lookup="project")
projects_router.register(r"tasks", TaskViewSet, basename="project-tasks")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(projects_router.urls)),
]
