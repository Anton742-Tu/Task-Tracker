from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "department",
            "position",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Создание пользователя с хешированием пароля."""
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
