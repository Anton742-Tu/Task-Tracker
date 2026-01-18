from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.files.models import FileAttachment
from apps.users.models import User
from apps.users.permissions import IsAdminUser, IsManagerOrAdmin

from .serializers import (
    FileAttachmentSerializer,
    FileUpdateSerializer,
    FileUploadSerializer,
)


class FileUploadView(APIView):
    """View для загрузки файлов"""

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            file_attachment = serializer.save()

            # Возвращаем данные о загруженном файле
            response_serializer = FileAttachmentSerializer(
                file_attachment, context={"request": request}
            )

            return Response(
                {"message": "Файл успешно загружен", "file": response_serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileListView(generics.ListAPIView):
    """Список файлов с фильтрацией"""

    serializer_class = FileAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = FileAttachment.objects.all()

        # Фильтрация по задачам
        task_id = self.request.query_params.get("task_id")
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        # Фильтрация по проектам
        project_id = self.request.query_params.get("project_id")
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # Фильтрация по пользователям
        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Фильтрация по типу файла
        file_type = self.request.query_params.get("file_type")
        if file_type:
            queryset = queryset.filter(file_type=file_type)

        # Фильтрация по публичным файлам или файлам пользователя
        if user.is_admin:
            # Админы видят все файлы
            return queryset

        # Менеджеры видят файлы своих проектов и публичные файлы
        if user.is_manager:
            return queryset.filter(
                Q(is_public=True)
                | Q(project__members=user)
                | Q(project__creator=user)
                | Q(uploaded_by=user)
            ).distinct()

        # Сотрудники видят только свои файлы и публичные файлы
        return queryset.filter(
            Q(is_public=True)
            | Q(uploaded_by=user)
            | Q(task__assignee=user)
            | Q(project__members=user)
        ).distinct()


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали, обновление и удаление файла"""

    queryset = FileAttachment.objects.all()
    serializer_class = FileAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return FileUpdateSerializer
        return FileAttachmentSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            # Для изменения/удаления нужны особые права
            return [IsManagerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
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

        if user.is_manager:
            return FileAttachment.objects.filter(
                Q(is_public=True)
                | Q(project__members=user)
                | Q(project__creator=user)
                | Q(uploaded_by=user)
            ).distinct()

        return FileAttachment.objects.filter(
            Q(is_public=True)
            | Q(uploaded_by=user)
            | Q(task__assignee=user)
            | Q(project__members=user)
        ).distinct()


class FileDownloadView(APIView):
    """View для скачивания файла"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        file_attachment = get_object_or_404(FileAttachment, pk=pk)

        # Проверяем права доступа
        user = request.user
        can_access = False

        if user.is_admin:
            can_access = True
        elif file_attachment.is_public:
            can_access = True
        elif user == file_attachment.uploaded_by:
            can_access = True
        elif file_attachment.task and file_attachment.task.assignee == user:
            can_access = True
        elif (
            file_attachment.project
            and file_attachment.project.members.filter(id=user.id).exists()
        ):
            can_access = True

        if not can_access:
            return Response(
                {"error": "Нет доступа к этому файлу"}, status=status.HTTP_403_FORBIDDEN
            )

        # Открываем файл для чтения
        try:
            file = open(file_attachment.file.path, "rb")
            response = Response(file)

            # Устанавливаем заголовки для скачивания
            response["Content-Disposition"] = (
                f'attachment; filename="{file_attachment.original_filename}"'
            )
            response["Content-Type"] = file_attachment.mime_type
            response["Content-Length"] = file_attachment.file_size

            return response
        except FileNotFoundError:
            return Response(
                {"error": "Файл не найден на сервере"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StorageStatsView(APIView):
    """Статистика использования хранилища"""

    permission_classes = [IsAdminUser]

    def get(self, request):
        from django.db.models import Count, Sum

        stats = FileAttachment.objects.aggregate(
            total_files=Count("id"),
            total_size=Sum("file_size"),
            image_count=Count("id", filter=Q(file_type="image")),
            document_count=Count("id", filter=Q(file_type="document")),
        )

        # Добавляем человекочитаемый размер
        total_size = stats["total_size"] or 0
        stats["total_size_human"] = self._human_readable_size(total_size)

        # Статистика по пользователям
        user_stats = (
            FileAttachment.objects.values("uploaded_by__username")
            .annotate(file_count=Count("id"), total_size=Sum("file_size"))
            .order_by("-total_size")[:10]
        )

        return Response(
            {
                "storage_stats": stats,
                "top_users": user_stats,
            }
        )

    def _human_readable_size(self, size):
        """Конвертируем размер в человекочитаемый формат"""
        for unit in ["Б", "КБ", "МБ", "ГБ"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} ТБ"
