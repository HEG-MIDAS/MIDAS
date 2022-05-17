import json
import os
import mimetypes
import django
import datetime
from wsgiref import headers
import requests
from django.http import HttpRequest, HttpResponse, Http404, JsonResponse
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from os import listdir
from os.path import isfile, join, splitext
from .forms import DateSelection, TokenForm
from .models import GroupOfFavorite, Favorite, Token, Source
from MIDAS_app.models import Favorite, User
from django.middleware import csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
import random
from MIDAS_api.views import *
from rest_framework.request import Request
from django.contrib import messages
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

    # new_request = Request(request)
    # new_request.method = 'GET'
    # request.GET._mutable = True
    # new_request.query_params['format'] = 'json'
    # request.GET._mutable = False
    # print(StatusView().get(new_request).data)

    new_request = Request(request)
    new_request.method = 'POST'
    new_request.data['sources'] = ['climacity']
    new_request.data['stations'] = ['prairie']
    new_request.data['parameters'] = ['tamb_avg']
    new_request.data['start_date'] = '2022-05-08 00:00:00'
    new_request.data['end_date'] = '2022-05-08 23:59:59'

    new_request.user = request.user

    print(SearchView().post(new_request).data)

    context['sources'] = [{'name': source['name'], 'slug': source['slug']} for source in json.loads(requests.get('http://localhost:8000/api/sources/').content.decode())]
    

    # csrftoken = django.middleware.csrf.get_token(request)
    # print(csrftoken)
    # print(requests.post('http://localhost:8000/api/filter/', headers={"X-CSRFToken": csrftoken}))
    return render(request, 'index.html', context)


@require_http_methods(["POST"])
def stations_dashboard(request):
    data = []

    jsonData = json.loads(request.body)
    sources = jsonData.get('sources')

    request_user = request.user

    request = HttpRequest()
    new_request = Request(request)
    new_request.method = 'POST'
    new_request.data['sources'] = sources

    new_request.user = request_user

    data_stations_response = json.loads(json.dumps(FilterView().post(new_request).data))
    for station in data_stations_response:
        data.append({'source': station['source'], 'name': station['name'], 'slug': station['slug']})

    return JsonResponse(json.dumps(data), safe=False)

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
        try:
            tk = Token.objects.get(name=request.POST["name"])
            post_form = TokenForm(request.POST,instance=tk)
            if post_form.is_valid():
                tk = post_form.save(request.user)
                messages.info(request,"Le token a bien été actualisé",extra_tags="message")
                return redirect('account_token')
        except:
            post_form = TokenForm(request.POST)
            if post_form.is_valid():
                tk = post_form.save(request.user)
                messages.info(request,tk,extra_tags="token")
                return redirect('account_token')
            else:
                # assign
                messages.info(request,post_form.errors,extra_tags="form")
                return redirect('account_token')

    storage = messages.get_messages(request)
    for message in storage:
        if message.extra_tags == "form":
            context['form'].errors = message
        else:
            context[message.extra_tags] = message
    return render(request, 'manage_token.html',context)

@login_required
def manage_data(request):

    media_path = join(settings.MEDIA_ROOT, join(request.GET.get('origin', ''), request.GET.get('source', '')))
    sources_input = Source.objects.all()
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
            'sources_input':sources_input,
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
@require_http_methods(["POST"])
def harvest_data(request):
    print(request.POST)
    if 'updateOperation' in request.POST and request.POST['updateOperation'] == 'files':
        if 'starting_date' in request.POST and 'ending_date' in request.POST and request.POST['starting_date'] != "" and request.POST['ending_date'] != "":
            source_dict = {
                "climacity": "python3 {}/climacity.py -s {} -e {}".format(settings.CLIMACITY_ROOT, str(request.POST['starting_date']), str(request.POST['ending_date'])),
                "sabra" : "python3 {}/sabra.py -s {} -e {}".format(settings.SABRA_ROOT, str(request.POST['starting_date']), str(request.POST['ending_date']))
            }
            if 'source_list' in request.POST:
                for s in request.POST.getlist('source_list'):
                    if s in source_dict:
                        print("Launching {}".format(s))
                        print("{}".format(os.system(source_dict[s])))
    elif request.POST['updateOperation'] == 'db':
        print("Updating Database...")
        print("{}".format(os.system("python3 MIDAS/manage.py insert_ssp_db")))
    elif request.POST['updateOperation'] == 'dbInfos':
        print("Updating Databse Informations...")
        print("{}".format(os.system("python3 MIDAS/manage.py update_db_params_infos")))

    return redirect(manage_data)
