import os
import mimetypes
import django
from wsgiref import headers
import requests
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from os import listdir
from os.path import isfile, join, splitext
from .forms import DateSelection
from .models import GroupOfFavorite, Favorite
from MIDAS_app.models import Favorite, User
from django.middleware import csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
import random
from . import update_db

@csrf_protect
@require_http_methods(["POST"])
def test(request):
    data = requests.post('http://localhost:8000/api/filter/')
    print(request.session.session_key)
    if(request.user.is_anonymous == False):
        return HttpResponse(data)
    else:
        return HttpResponse('{"data":"error"}')

def index(request):
    # user = User.objects.first()
    # groupfav = user.group_of_favorite.all()
    # print(groupfav)
    # fav = groupfav[0].favorite.all()
    # print(fav)
    # f = fav[0]
    # field_object = Favorite._meta.get_field('paramaters_of_station')
    # field_value = field_object.value_from_object(f)
    # print(field_value)
    # request.session["TEST"] = random.randint(0,100)
    context = {}

    # csrftoken = django.middleware.csrf.get_token(request)
    # print(csrftoken)
    # print(requests.post('http://localhost:8000/api/filter/', headers={"X-CSRFToken": csrftoken}))
    return render(request, 'index.html', context)

def statut(request):
    context = {}
    return render(request, 'statut.html', context)

def statut_badge(request, source):
    dic = {'SABRA':'https://www.ropag-data.ch/gechairmo/i_extr.php','ClimaCity':'http://www.climacity.org/Axis/'}
    for k in dic:
        if(source.lower() in k.lower()):
            url = dic[k]
            context = {'source':k}
            try:
                resp = requests.get(url)
                if resp.status_code == 200:
                    context['msg'] = 'ok'
                else:
                    context['msg'] = 'error'
                return render(request, 'includes/statut_badge.html', context, 'image/svg+xml')
            except:
                context['msg'] = 'error'
                return render(request, 'includes/statut_badge.html', context, 'image/svg+xml')

    else:
        raise Http404

@login_required
def favorite_profile(request):
    user_favorites_group = GroupOfFavorite.objects.filter(user=request.user.id)
    context = {
        'list': user_favorites_group
    }
    return render(request, 'favorites.html',context)
@login_required
def manage_data(request):

    media_path = join(settings.MEDIA_ROOT, join(request.GET.get('origin', ''), request.GET.get('source', '')))

    if request.method == 'POST':
        if request.POST.get('filename', '') != '':
            media_path = join(settings.MEDIA_ROOT, join(request.POST.get('origin', ''), request.POST.get('source', '')))
            file_path = join(media_path, request.POST.get('filename', ''))
            data_file = open(file_path, 'r')
            mime_type, _ = mimetypes.guess_type(file_path)
            response = HttpResponse(data_file, content_type=mime_type)
            response['Content-Disposition'] = "attachment; filename={}".format(request.POST['filename'])
            return response

    else:
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

        form = DateSelection
        context = {
            'file': folder_files,
            'origin': request.GET.get('origin', ''),
            'source': request.GET.get('source', ''),
            'path_redirect': path_redirect,
            'form': form,
        }
        return render(request, 'manage_data.html', context)


@user_passes_test(lambda u: u.is_superuser)
def harvest_data(request):
    if request.method == 'POST':
        print("Climacity : {}".format(os.system("python3 {}/climacity.py -s {} -e {}".format(settings.CLIMACITY_ROOT, str(request.POST['starting_date']), str(request.POST['ending_date'])))))
        print("SABRA : {}".format(os.system("python3 {}/scrap.py -s {} -e {}".format(settings.SABRA_ROOT, str(request.POST['starting_date']), str(request.POST['ending_date'])))))
    return redirect(manage_data)
