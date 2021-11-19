from django.urls import path

from .views import index, registration, upload_file, show_not_private_files, show_owner_files, download_file, \
    upload_keys, generate_keys, show_keys, delete_keys

urlpatterns = [
    path('', index, name='index'),
    path('registration/', registration, name='registration'),
    path('upload_file/', upload_file, name='upload_file'),
    path('files/', show_not_private_files, name='files'),
    path('my_files/', show_owner_files, name='user_files'),
    path('download/', download_file, name='download'),
    path('upload_keys/', upload_keys, name='upload_keys'),
    path('generate_keys/', generate_keys, name='generate_keys'),
    path('show_keys/', show_keys, name='show_keys'),
    path('delete_keys/', delete_keys, name='delete_keys'),
]
