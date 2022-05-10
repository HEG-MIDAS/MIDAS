import json
import os
import mimetypes
import django
import datetime
from wsgiref import headers
import requests
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from os import listdir
from os.path import isfile, join, splitext
from .forms import DateSelection, TokenForm
from .models import GroupOfFavorite, Favorite, Token
from MIDAS_app.models import Favorite, User
from django.middleware import csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
import random
from MIDAS_api.views import StatusView, SearchView
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
    # update_db.update_sources()
    # update_db.update_stations()
    # update_db.update_parameters()
    context = {}

    # request.GET._mutable = True
    # request.GET['format'] = 'json'
    # request.GET._mutable = False
    # print(StatusView.as_view()(request).rendered_content.decode())

    # new_request = HttpRequest()
    # new_request.method = 'POST'
    # new_request.POST = json.dumps({
    #     "sources": ["climacity"],
    #     "stations": ["prairie"],
    #     "parameters": ["tamb_avg"],
    #     "start_date": "2022-05-08 00:00:00",
    #     "end_date": "2022-05-08 23:59:59"
    # })
    # new_request.POST['sources'] = ['climacity']

    # new_request.user = request.user

    # print(SearchView().post(new_request))

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
@require_http_methods(["POST"])
def favorite_deletion(request,slug):
    user_favorites_group = GroupOfFavorite.objects.filter(user=request.user.id).filter(slug=slug).delete()
    return redirect(manage_favorite)

@login_required
def manage_favorite(request):
    user_favorites_group = GroupOfFavorite.objects.filter(user=request.user.id)
    list = {}
    i = 0
    for g in user_favorites_group:
        list[i] = {
            'name': g.name,
            'slug': g.slug,
            'favorites': []
        }
        for f in g.favorite.all():
            stations = []
            params = []
            for p in f.parameters_of_station.all():
                if p.station.name not in stations:
                    stations.append(p.station.name)
                if p.parameter.name not in params:
                    params.append(p.parameter.name)
            list[i]['favorites'].append({
                'id': f.id,
                'starting_date':datetime.datetime.strftime(f.starting_date,'%Y-%m-%d'),
                'ending_date':datetime.datetime.strftime(f.ending_date,'%Y-%m-%d'),
                'stations':stations,
                'parameters':params
            })
        i+=1
    context = {
        'list': list
    }
    return render(request, 'favorites.html',context)


@login_required
@require_http_methods(["POST"])
def token_deletion(request,slug):
    user_favorites_group = Token.objects.filter(user=request.user.id).filter(slug=slug).delete()
    return redirect(manage_token)

@login_required
def manage_token(request):
    tokens = Token.objects.filter(user=request.user.id)
    context = {
        'form': TokenForm,
        'list': tokens
    }
    if request.method == 'POST':
        post_form = TokenForm(request.POST)
        if post_form.is_valid():
            tk = post_form.save(request.user)
            context['token']=tk
        else:
            context['form']=post_form

    return render(request, 'manage_token.html',context)

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
        folder_flavours = {}
        for e in listdir(media_path):
            if not isfile(join(media_path, e)):
                folder_files[e] = False
                if e == 'transformed':
                    folder_flavours[e] = 'Données transformées'
                elif e == 'original':
                    folder_flavours[e] = 'Données originelles'
                else:
                    folder_flavours[e] = e
            elif splitext(e)[1] in [".csv", ".txt"]:
                folder_files[e] = True
                folder_flavours[e] = e

        path_redirect = ''
        if request.GET.get('origin', '') != '':
            if request.GET.get('source', '') != '':
                pass
            else:
                path_redirect = '?origin={}&source='.format(request.GET.get('origin', ''))
        else:
            path_redirect = '?origin='

        originFlavourText = 'Données transformées' if request.GET.get('origin', '') == 'transformed' else 'Données originelles'
        form = DateSelection
        context = {
            'file': folder_files,
            'file_flavour': folder_flavours,
            'origin': request.GET.get('origin', ''),
            'origin_flavour': originFlavourText,
            'source': request.GET.get('source', ''),
            'path_redirect': path_redirect,
            'form': form,
        }
        return render(request, 'manage_data.html', context)


@user_passes_test(lambda u: u.is_superuser)
def harvest_data(request):
    if request.method == 'POST':
        print("LAUNCHED")
        print("Climacity : {}".format(os.system("python3 {}/climacity.py -s {} -e {}".format(settings.CLIMACITY_ROOT, str(request.POST['starting_date']), str(request.POST['ending_date'])))))
        print("CLIMACITY DONE")
        print("SABRA : {}".format(os.system("python3 {}/sabra.py -s {} -e {}".format(settings.SABRA_ROOT, str(request.POST['starting_date']), str(request.POST['ending_date'])))))
    return redirect(manage_data)
