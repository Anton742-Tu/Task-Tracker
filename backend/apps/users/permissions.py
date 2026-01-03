from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Только администраторы"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class IsManagerOrAdmin(permissions.BasePermission):
    """Менеджеры или администраторы"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_manager
            or request.user.is_admin
            or request.user.is_superuser
        )


class IsEmployeeOrHigher(permissions.BasePermission):
    """Сотрудники, менеджеры или администраторы"""

    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsProjectMember(permissions.BasePermission):
    """Участник проекта или выше"""

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Администраторы и менеджеры видят все
        if user.is_admin or user.is_manager or user.is_superuser:
            return True

        # Проверяем, является ли пользователь участником проекта
        # Для объекта Project
        if hasattr(obj, "members"):
            return obj.members.filter(id=user.id).exists() or obj.creator == user

        # Для объекта Task (через проект)
        if hasattr(obj, "project"):
            return (
                obj.project.members.filter(id=user.id).exists()
                or obj.project.creator == user
            )

        # Для других объектов
        return False
