from django.urls import path

from .views import index, registration

urlpatterns = [
    path('', index, name='index'),
    path('registration/', registration, name='registration'),
]
