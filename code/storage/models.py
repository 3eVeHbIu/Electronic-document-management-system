from datetime import datetime
from os.path import splitext

from django.contrib.auth.models import User
from django.core import validators
from django.db import models


def doc_path(instance, filename):
    return f'user_{instance.owner.id}/doc/{datetime.now().timestamp()}{splitext(filename)[1]}'


def signature_path(instance, filename):
    return f'user_{instance.owner.id}/doc/{splitext(instance.file.file.split("/")[-1])[0]}.signature'


def private_key_path(instance, filename):
    return f'user_{instance.owner.id}/keys/key'


def public_key_path(instance, filename):
    return f'user_{instance.owner.id}/keys/key.pub'


class Files(models.Model):
    owner = models.ForeignKey(
        User,
        verbose_name='Владелец',
        editable=False,
        on_delete=models.CASCADE,
    )
    original_filename = models.CharField(
        verbose_name='Имя файла пользователя',
        max_length=128,
        blank=False,
        null=False,
        validators=[
            validators.MinLengthValidator(5),
            validators.ProhibitNullCharactersValidator(),
        ],
        error_messages={
            'min_length': 'Слишком короткое название',
            'null_characters_not_allowed': 'Вы не можете использовать null символ в названии',
        }
    )
    file = models.FileField(
        default=None,
        verbose_name='Файл',
        upload_to=doc_path,
        blank=False,
        null=False
    )
    is_private = models.BooleanField(
        default=False,
        null=False,
        blank=False,
    )
    is_signed = models.BooleanField(
        default=False,
        null=False,
        blank=False,
    )
    signature = models.FileField(
        default=None,
        verbose_name='Сигнатура',
        upload_to=signature_path,
        blank=True,
        null=True,
    )
    add_date_time = models.DateTimeField(
        verbose_name='Дата добавления файла в систему',
        default=datetime.now(),
    )
    editing_date_time = models.DateTimeField(
        verbose_name='Дата последней редакции файла',
        default=datetime.now(),
    )

    class Meta:
        unique_together = ('owner', 'original_filename')
        verbose_name_plural = 'Файлы'
        verbose_name = 'Файл'
        ordering = ['-editing_date_time']
        get_latest_by = '-add_date_time'


class Keys(models.Model):
    owner = models.ForeignKey(
        User,
        verbose_name='Владелец',
        editable=False,
        on_delete=models.CASCADE,
    )
    private_key = models.FileField(
        default=None,
        verbose_name='Приватный ключ',
        upload_to=private_key_path,
        blank=False,
        null=False
    )
    public_key = models.FileField(
        default=None,
        verbose_name='Публичный ключ',
        upload_to=public_key_path,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name_plural = 'ключи'
        verbose_name = 'ключ'
        ordering = ['owner']
        get_latest_by = '-owner'
