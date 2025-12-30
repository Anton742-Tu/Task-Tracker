from django.contrib.auth import get_user_model
from rest_framework import viewsets

from api.permissions import IsAdminUser
from api.serializers.auth import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """API для управления пользователями (только для администраторов)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """Администраторы видят всех пользователей"""
        user = self.request.user
        if user.is_admin:
            return User.objects.all()
        return User.objects.none()
