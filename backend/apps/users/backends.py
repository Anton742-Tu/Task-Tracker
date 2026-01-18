from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class RoleBasedAdminBackend(ModelBackend):
    def has_module_permission(self, user_obj, app_label):
        """Разрешить доступ к админке менеджерам и админам"""
        if user_obj.is_authenticated:
            return user_obj.role in ["manager", "admin"]
        return False

    def has_perm(self, user_obj, perm, obj=None):
        """Разрешения на основе ролей"""
        if user_obj.is_authenticated:
            if user_obj.role == "admin":
                return True
            elif user_obj.role == "manager":
                # Менеджеры могут управлять проектами и задачами
                return perm in [
                    "projects.view_project",
                    "projects.add_project",
                    "projects.change_project",
                    "projects.delete_project",
                    "tasks.view_task",
                    "tasks.add_task",
                    "tasks.change_task",
                    "tasks.delete_task",
                    "users.view_user",
                ]
        return False
