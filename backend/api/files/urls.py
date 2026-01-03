from django.urls import path

from .views import (FileDetailView, FileDownloadView, FileListView,
                    FileUploadView, StorageStatsView)

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path("", FileListView.as_view(), name="file-list"),
    path("<int:pk>/", FileDetailView.as_view(), name="file-detail"),
    path("<int:pk>/download/", FileDownloadView.as_view(), name="file-download"),
    path("stats/", StorageStatsView.as_view(), name="storage-stats"),
]
