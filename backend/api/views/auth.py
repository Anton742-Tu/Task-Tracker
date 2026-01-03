from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.serializers.auth import RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterView(APIView):
    """Регистрация нового пользователя"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Создаем токены для нового пользователя
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "message": "Пользователь успешно зарегистрирован",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Выход из системы (отзыв токена)"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"message": "Вы успешно вышли из системы"},
                    status=status.HTTP_205_RESET_CONTENT,
                )
            return Response(
                {"error": "Токен не предоставлен"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """Получение и обновление профиля текущего пользователя"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Обновление профиля"""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # Проверяем, не пытается ли пользователь изменить свою роль
            if "role" in serializer.validated_data and not user.is_admin:
                return Response(
                    {"error": "Вы не можете изменять свою роль"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Кастомный view для получения токена с дополнительной информацией
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Получаем пользователя по username из запроса
            user = User.objects.get(username=request.data.get("username"))
            response.data["user"] = UserSerializer(user).data
        return response
