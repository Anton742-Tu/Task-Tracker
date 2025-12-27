from rest_framework import permissions


class IsProjectMember(permissions.BasePermission):
    """Проверяет, что пользователь является участником проекта."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "project"):
            return obj.project.members.filter(id=request.user.id).exists()
        if hasattr(obj, "members"):
            return obj.members.filter(id=request.user.id).exists()
        return False


class IsTaskAssigneeOrCreator(permissions.BasePermission):
    """Проверяет, что пользователь исполнитель или создатель проекта задачи."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        is_assignee = obj.assignee == request.user if obj.assignee else False
        is_project_creator = obj.project.creator == request.user
        return is_assignee or is_project_creator


class IsProjectCreator(permissions.BasePermission):
    """Проверяет, что пользователь создатель проекта."""

    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user
