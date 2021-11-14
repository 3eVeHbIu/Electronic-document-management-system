import os
import urllib

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .forms import UserForm, FileForm
from .models import Files


@login_required()
def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'storage/index.html')


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
def file_upload(request):
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
            return render(request, 'storage/file_upload.html', context)
    else:
        form = FileForm()
        context = {'form': form}
        return render(request, 'storage/file_upload.html', context)


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
    filename = request.GET['file']
    owner = request.GET['owner']
    owner_id = User.objects.get(username=owner).id
    file = Files.objects.get(original_filename=filename, owner=owner_id)
    if str(owner) == str(file.owner) or not file.is_private:
        file = file.file.name
        file_path = os.path.join(settings.MEDIA_ROOT, file)
        content_types = {
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(
                    f.read(),
                    content_type=content_types[filename.split('.')[-1]]
                )
                response['Content-Disposition'] = "inline; filename=*" + urllib.parse.quote(filename)
                return response
        else:
            return HttpResponse(file_path)
    else:
        return HttpResponse(f'{type(owner)} {type(file.owner)} {str(owner) == str(file.owner)}')
    raise Http404


def not_found_response(request, exception):
    return render(request, 'storage/404.html')
