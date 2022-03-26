from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from os import listdir

def index(request):
    context = {}
    return render(request, 'index.html',context)

@login_required
def manage_data(request):
    media_path = settings.MEDIA_ROOT
    test = listdir(media_path)
    context = {'file':test}
    return render(request, 'manage_data.html',context)
