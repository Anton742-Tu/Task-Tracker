from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("create/", views.create_task, name="create_task"),
    path("", views.task_list, name="task_list"),
    path("my/", views.my_tasks, name="my_tasks"),
    path("statistics/", views.task_statistics, name="statistics"),
    path("<int:task_id>/", views.task_detail, name="task_detail"),
    path("<int:task_id>/edit/", views.edit_task, name="edit_task"),
    path("<int:task_id>/delete/", views.delete_task, name="delete_task"),
    path(
        "<int:task_id>/change-status/", views.change_task_status, name="change_status"
    ),
]
