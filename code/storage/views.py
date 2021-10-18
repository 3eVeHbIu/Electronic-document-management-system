from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

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
    themes = Files.objects.all()
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
            context = {'form': form, 'errors': errors, 'themes': themes}
            return render(request, 'storage/file_upload.html', context)
    else:
        form = FileForm()
        context = {'form': form, 'themes': themes}
        return render(request, 'storage/file_upload.html', context)
