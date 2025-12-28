from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from api.views.home import home_view

schema_view = get_schema_view(
    openapi.Info(
        title="Task Tracker API",
        default_version="v1",
        description="API для системы управления задачами",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@tasktracker.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Главная страница
    path("", home_view, name="home"),
    # Админка
    path("admin/", admin.site.urls),
    # API
    path("api/", include("api.urls")),
    # Документация
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# Debug toolbar только для разработки
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
