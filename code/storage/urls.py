from django.urls import path

from .views import index, registration, file_upload, show_not_private_files, show_owner_files, download_file

urlpatterns = [
    path('', index, name='index'),
    path('registration/', registration, name='registration'),
    path('file_upload/', file_upload, name='file_upload'),
    path('files/', show_not_private_files, name='files'),
    path('my_files/', show_owner_files, name='user_files'),
    path('download/', download_file, name='download'),
]
