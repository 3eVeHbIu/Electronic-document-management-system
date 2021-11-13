from django import forms
from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError

from .models import Files


class UserForm(forms.ModelForm):
    error_css_class = 'is-invalid'
    required_css_class = 'is-valid'
    field_order = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')
    username = forms.CharField(
        label='Имя пользователя',
        min_length=4,
        widget=forms.widgets.TextInput(
            attrs={
                'placeholder': 'Ivan',
                'class': 'form-control'
            }
        )
    )
    email = forms.EmailField(
        label='Email',
        error_messages={'invalid': 'Введите корректный email'},
        widget=forms.widgets.EmailInput(
            attrs={
                'placeholder': 'ivan@mail.com',
                'class': 'form-control'
            }
        )
    )
    first_name = forms.CharField(
        label='Имя',
        min_length=2,
        validators=[validators.RegexValidator(regex='^([A-zА-я])+$')],
        error_messages={'invalid': 'Имя может содержать только Латиницу или Кириллицу'},
        widget=forms.widgets.TextInput(
            attrs={
                'placeholder': 'Иван',
                'class': 'form-control'
            }
        )
    )
    last_name = forms.CharField(
        label='Фамилия',
        min_length=2,
        validators=[validators.RegexValidator(regex='^([A-zА-я])+$')],
        error_messages={'invalid': 'Фамилия может содержать только Латиницу или Кириллицу'},
        widget=forms.widgets.TextInput(
            attrs={
                'placeholder': 'Иванов',
                'class': 'form-control'
            }
        )
    )
    password1 = forms.CharField(
        label='Пароль',
        min_length=6,
        widget=forms.widgets.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )
    password2 = forms.CharField(
        label='Повторить пароль',
        min_length=6,
        widget=forms.widgets.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2',)

    def clean(self):
        super().clean()
        errors = {}
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            errors['password1'] = ValidationError('Пароли не совпадают')
        if 'email' in self.cleaned_data:
            if User.objects.filter(email=self.cleaned_data['email']):
                errors['email'] = ValidationError('Email уже занят')
            if User.objects.filter(username=self.cleaned_data['username']):
                errors['username'] = ValidationError('Имя пользователя уже занято')
        if errors:
            raise ValidationError(errors)


class FileForm(forms.ModelForm):
    field_order = ('file', 'is_private')
    file = forms.FileField(
        label='Выберите файл',
        help_text='Можно загрузить только doc/docs',
        validators=[
            validators.FileExtensionValidator(allowed_extensions=('doc', 'docx')),
        ],
        error_messages={
            'invalid_extension': 'Данный формат файла не поддерживается'
        },
        widget=forms.widgets.FileInput(
            attrs={'class': 'form-control'}
        )
    )
    is_private = forms.BooleanField(
        label='Приватный',
        required=False,
        widget=forms.widgets.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )
    )

    class Meta:
        model = Files
        fields = ('file', 'is_private')
