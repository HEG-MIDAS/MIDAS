import os
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from os import listdir, path
from os.path import isfile, join, splitext
import mimetypes

def index(request):
    context = {}
    return render(request, 'index.html',context)

@login_required
def manage_data(request):
    
    media_path = join(settings.MEDIA_ROOT, join(request.GET.get('origin', ''), request.GET.get('source', '')))
    
    if request.method == "POST" and request.POST.get('filename', '') != '':
        media_path = join(settings.MEDIA_ROOT, join(request.POST.get('origin', ''), request.POST.get('source', '')))
        file_path = join(media_path, request.POST.get('filename', ''))
        data_file = open(file_path, 'r')
        mime_type, _ = mimetypes.guess_type(file_path)
        response = HttpResponse(data_file, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename={}".format(request.POST['filename'])
        return response

    folder_files = {}
    for e in listdir(media_path):
        if not isfile(join(media_path, e)):
            folder_files[e] = False
        elif splitext(e)[1] in [".csv", ".txt"]:
            folder_files[e] = True

    path_redirect = ''
    if request.GET.get('origin', '') != '':
        if request.GET.get('source', '') != '':
            pass
        else:
            path_redirect = '?origin={}&source='.format(request.GET.get('origin', ''))
    else:
        path_redirect = '?origin='

    context = {
        'file': folder_files,
        'origin': request.GET.get('origin', ''),
        'source': request.GET.get('source', ''),
        'path_redirect': path_redirect,
    }
    return render(request, 'manage_data.html', context)
