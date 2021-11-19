import os
import urllib

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from .forms import UserForm, FileForm, KeysForm
from .models import Files, Keys


@login_required()
def index(request):
    return redirect('files')


def registration(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('index')
            else:
                errors = UserForm.errors
                context = {'form': form, 'errors': errors}
                return render(request, 'registration/registration.html', context)
        else:
            form = UserForm()
            context = {'form': form}
            return render(request, 'registration/registration.html', context)


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.owner = request.user
            file.original_filename = request.FILES['file'].name
            file.save()
            return redirect('index')
        else:
            errors = UserForm.errors
            context = {'form': form, 'errors': errors}
            return render(request, 'storage/upload_file.html', context)
    else:
        form = FileForm()
        context = {'form': form}
        return render(request, 'storage/upload_file.html', context)


@login_required
def show_owner_files(request):
    files = Files.objects.filter(owner=request.user.id)
    context = {'files': files}
    return render(request, 'storage/owner_files.html', context)


@login_required
def show_not_private_files(request):
    files = Files.objects.filter(is_private=False)
    context = {'files': files}
    return render(request, 'storage/files.html', context)


@login_required
def download_file(request):
    if 'user' in request.GET:
        user = request.GET['user']
        user = User.objects.filter(username=user)
        if user:
            user = user[0]
            key = Keys.objects.filter(owner=user)
            if key:
                public = key[0].public_key.name
                public_path = os.path.join(settings.MEDIA_ROOT, public)
                content_type = 'application/octet-stream'
                if os.path.exists(public_path):
                    with open(public_path, 'rb') as f:
                        response = HttpResponse(f.read(), content_type=content_type)
                        response['Content-Disposition'] = f'inline; filename=*{user}.pub'
                    return response
    elif 'file' in request.GET and 'owner' in request.GET:
        filename = request.GET['file']
        owner = request.GET['owner']
        owner = User.objects.get(username=owner)
        file = Files.objects.get(original_filename=filename, owner=owner)
        if 'signature' in request.GET:
            if file.is_signed:
                signature = file.signature.name
                signature_path = os.path.join(settings.MEDIA_ROOT, signature)
                content_type = 'application/octet-stream'
                if os.path.exists(signature_path):
                    filename = os.path.splitext(filename)[0]
                    with open(signature_path, 'rb') as f:
                        response = HttpResponse(f.read(), content_type=content_type)
                        response['Content-Disposition'] = f'inline; filename=*{urllib.parse.quote(filename)}.signature'
                    return response
        elif str(owner) == str(file.owner) or not file.is_private:
            file = file.file.name
            file_path = os.path.join(settings.MEDIA_ROOT, file)
            content_types = {
                'doc': 'application/msword',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type=content_types[filename.split('.')[-1]])
                    response['Content-Disposition'] = "inline; filename=*" + urllib.parse.quote(filename)
                return response
    raise Http404


@login_required
def upload_keys(request):
    if request.method == 'POST':
        form = KeysForm(request.POST, request.FILES)
        if form.is_valid():
            keys = get_correct_object(request.user)
            keys.public_key = form.cleaned_data.get('public_key')
            keys.private_key = form.cleaned_data.get('private_key')
            keys.save()
            return redirect('show_keys')
        else:
            errors = UserForm.errors
            context = {'form': form, 'errors': errors}
            return render(request, 'storage/upload_keys.html', context)
    else:
        form = KeysForm()
        context = {'form': form}
        return render(request, 'storage/upload_keys.html', context)


@login_required
def generate_keys(request):
    keys = get_correct_object(request.user)
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.public_key().export_key()
    keys.private_key.save('key', ContentFile(private_key))
    keys.public_key.save('key.pub', ContentFile(public_key))
    return redirect('show_keys')


@login_required
def show_keys(request):
    keys = Keys.objects.filter(owner=request.user)
    if keys:
        keys = keys[0]
        private_path = os.path.join(settings.MEDIA_ROOT, keys.private_key.name)
        public_path = os.path.join(settings.MEDIA_ROOT, keys.public_key.name)
        with open(private_path, 'rb') as f:
            private = f.read().decode()
        with open(public_path, 'rb') as f:
            public = f.read().decode()
        context = {'private': private, 'public': public}
        return render(request, 'storage/show_keys.html', context)
    else:
        return redirect('upload_keys')


@login_required
def delete_keys(request):
    keys = Keys.objects.filter(owner=request.user)
    if keys:
        keys = keys[0]
        delete_file(keys.private_key.name)
        delete_file(keys.public_key.name)
        keys.delete()
    return redirect('upload_keys')


@login_required
def sign_file(request):
    filename = request.GET['file']
    owner = request.GET['owner']
    owner = User.objects.get(username=owner)
    file = Files.objects.filter(original_filename=filename, owner=owner)
    if not file:
        raise Http404
    file = file[0]
    if str(owner) != str(file.owner):
        raise Http404
    if file.is_signed:
        return redirect('user_files')
    keys = Keys.objects.filter(owner=request.user)
    if not keys:
        return redirect('upload_keys')
    file = Files.objects.get(original_filename=filename, owner=owner)
    private = keys[0].private_key.name
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
    private_path = os.path.join(settings.MEDIA_ROOT, private)
    if os.path.exists(file_path) and os.path.exists(private_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        with open(private_path, 'rb') as f:
            private = f.read()
        key = RSA.importKey(private)
        hash = SHA256.new(content)
        signer = pkcs1_15.new(key)
        signature = signer.sign(hash)
        file.signature.save('signature', ContentFile(signature))
        file.is_signed = True
        file.save()
        return redirect('user_files')


def delete_file(file):
    file_path = os.path.join(settings.MEDIA_ROOT, file)
    if os.path.exists(file_path):
        os.remove(file_path)


def get_correct_object(owner):
    keys = Keys.objects.filter(owner=owner)
    if keys:
        keys = keys[0]
        delete_file(keys.private_key.name)
        delete_file(keys.public_key.name)
    else:
        keys = Keys()
        keys.owner = owner
    return keys


def not_found_response(request, exception):
    return render(request, 'storage/404.html')
