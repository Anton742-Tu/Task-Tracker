from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.employee_dashboard, name="employee_dashboard"),
    path("profile/", views.employee_profile, name="employee_profile"),
]
