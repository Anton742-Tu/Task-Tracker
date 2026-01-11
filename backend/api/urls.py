from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.views.auth import (
    CustomTokenObtainPairView,
    LogoutView,
    RegisterView,
    UserProfileView,
)
from api.views.home import home_view
from api.views.project import ProjectViewSet
from api.views.task import TaskViewSet
from api.views.user import UserViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"tasks", TaskViewSet)
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    # Аутентификация
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", UserProfileView.as_view(), name="user_profile"),
    path("files/", include("api.files.urls")),
    # API
    path("", include(router.urls)),
    # Диагностика (публичный доступ)
    path("diagnostic/", home_view, name="api-diagnostic"),
]
