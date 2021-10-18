from django.urls import path

from .views import index, registration, file_upload

urlpatterns = [
    path('', index, name='index'),
    path('registration/', registration, name='registration'),
    path('file_upload/', file_upload, name='file_upload'),
]
