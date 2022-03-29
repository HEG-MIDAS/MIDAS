import os
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from os import listdir, path
from os.path import isfile, join

def index(request):
    context = {}
    return render(request, 'index.html',context)

@login_required
def manage_data(request):
    media_path = settings.MEDIA_ROOT
    files = []
    for dir in listdir(media_path):
        for d in listdir(join(media_path, dir)):
            for file in listdir(join(media_path, join(dir, d))):
                if os.path.splitext(file)[1] in [".csv", ".txt"]:
                    files.append(join(dir, join(d, file)))

    context = {'file': files}
    return render(request, 'manage_data.html',context)
