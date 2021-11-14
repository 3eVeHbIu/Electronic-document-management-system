from datetime import datetime
from os.path import splitext

from django.contrib.auth.models import User
from django.core import validators
from django.db import models


class Themes(models.Model):
    name = models.CharField(
        max_length=32,
        db_index=True,
        verbose_name='Тематика',
    )

    class Meta:
        verbose_name_plural = 'Тематики'
        verbose_name = 'Тематика'
        ordering = ['name']

    def __str__(self):
        return self.name


def get_timestamp_path(instance, filename):
    return '%s%s' % (datetime.now().timestamp(), splitext(filename)[1])


class Files(models.Model):
    owner = models.ForeignKey(
        User,
        verbose_name='Владелец',
        help_text='Введите название новости',
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
        upload_to=get_timestamp_path,
        blank=False,
        null=False
    )
    is_private = models.BooleanField(
        default=False,
        null=False,
        blank=False,
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
