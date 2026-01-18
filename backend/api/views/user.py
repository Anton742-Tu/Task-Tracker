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
        # Проверяем, не является ли это фейковым представлением для генерации схемы
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()  # Возвращаем пустой queryset

        # Безопасная проверка is_admin
        if hasattr(user, "is_admin") and user.is_admin:
            return User.objects.all()

        # Для аутентифицированных не-админов
        if user.is_authenticated:
            return User.objects.filter(id=user.id)

        # Для анонимных пользователей
        return User.objects.none()
