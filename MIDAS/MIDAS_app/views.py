import json
import os
import mimetypes
import django
import datetime
from wsgiref import headers
import requests
from django.http import HttpRequest, HttpResponse, FileResponse, Http404, JsonResponse
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from os import listdir
from os.path import isfile, join, splitext
from .forms import DateSelection, TokenForm, RegisterForm
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
import time
from django.contrib.gis.geoip2 import GeoIP2

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    g = GeoIP2()
    try:
        location = g.city(ip)
        location_country = location["country_name"]
        location_city = location["city"]
    except:
        location_country = "Couldn't determine country"
        location_city = "Couldn't determine city"

    print(f"User IP Address : {''.join(ip)} | Country : {location_country} | City : {location_city} | Path : {request.path} | User : {request.user} | Method : {request.method}")

@csrf_protect
@require_http_methods(["POST"])
def test(request):
    get_ip(request)
    data = requests.post('http://localhost:8000/api/filter/')
    print(request.session.session_key)
    if(request.user.is_anonymous == False):
        return HttpResponse(data)
    else:
        return HttpResponse('{"data":"error"}')

def index(request):
    get_ip(request)
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

    # new_request = Request(request)
    # new_request.method = 'POST'
    # new_request.data['sources'] = ['climacity']
    # new_request.data['stations'] = ['prairie']
    # new_request.data['parameters'] = ['tamb_avg']
    # new_request.data['start_date'] = '2022-05-08 00:00:00'
    # new_request.data['end_date'] = '2022-05-08 23:59:59'

    # new_request.user = request.user

    # print(SearchView().post(new_request).data)
    context['sources'] = []
    try:
        context['sources'] = [{'name': source['name'], 'slug': source['slug']} for source in json.loads(requests.get('http://localhost:8000/api/sources/').content.decode())]
    except:
        pass

    if request.session.get('accountCreated'):
        context['accountCreated'] = True
        del request.session['accountCreated']

    # csrftoken = django.middleware.csrf.get_token(request)
    # print(csrftoken)
    # print(requests.post('http://localhost:8000/api/filter/', headers={"X-CSRFToken": csrftoken}))
    return render(request, 'index.html', context)


@require_http_methods(["POST"])
def stations_dashboard(request):
    get_ip(request)
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


@require_http_methods(["POST"])
def parameters_dashboard(request):
    get_ip(request)
    data = []

    jsonData = json.loads(request.body)
    sources = jsonData.get('sources')
    stations = jsonData.get('stations')

    request_user = request.user

    request = HttpRequest()
    new_request = Request(request)
    new_request.method = 'POST'
    new_request.data['sources'] = sources
    new_request.data['stations'] = stations

    new_request.user = request_user

    data_parameters_response = json.loads(json.dumps(FilterView().post(new_request).data))
    for parameter in data_parameters_response:
        stations_tmp = []
        sources_tmp = []
        for station in parameter['stations']:
            stations_tmp.append(station['slug'])
            sources_tmp.append(station['source']['slug'])

        data.append({'source': ','.join(sources_tmp), 'station': ','.join(stations_tmp), 'name': parameter['name'], 'slug': parameter['slug'], 'infos': parameter['infos']})

    return JsonResponse(json.dumps(data), safe=False)


@require_http_methods(["POST"])
def request_data_dasboard(request):
    get_ip(request)
    data = []

    jsonData = json.loads(request.body)
    sources = jsonData.get('sources')
    stations = jsonData.get('stations')
    parameters = jsonData.get('parameters')
    starting_date = jsonData.get('starting_date')
    ending_date = jsonData.get('ending_date')

    request_user = request.user

    request = HttpRequest()
    new_request = Request(request)
    new_request.method = 'POST'
    new_request.data['sources'] = sources
    new_request.data['stations'] = stations
    new_request.data['parameters'] = parameters
    new_request.data['start_date'] = starting_date
    new_request.data['end_date'] = ending_date

    new_request.user = request_user

    data_stations_response = json.loads(json.dumps(SearchView().post(new_request).data))
    formatted_data = {}

    for source in data_stations_response:
        formatted_data_source = {}
        for station in data_stations_response[str(source)]:
            formatted_data_station = {}
            last_hour = time.strftime("%Y-%m-%d %H:%M:%S")
            for hour in data_stations_response[str(source)][str(station)]:
                for parameter in data_stations_response[str(source)][str(station)][str(hour)]:
                    if str(parameter) not in formatted_data_station:
                        formatted_data_station[str(parameter)] = [[hour, data_stations_response[str(source)][str(station)][str(hour)][str(parameter)]]]
                        # print("If : " + hour)
                    else:
                        #if formatted_data_station[str(parameter)][-1] != [] and (datetime.datetime.strptime(hour, '%Y-%m-%d %H:%M:%S')-datetime.datetime.strptime(formatted_data_station[str(parameter)][-1][0], '%Y-%m-%d %H:%M:%S')) == datetime.timedelta(hours=1):
                        while (datetime.datetime.strptime(last_hour, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=1) < datetime.datetime.strptime(hour, '%Y-%m-%d %H:%M:%S')):
                            last_hour = (datetime.datetime.strptime(last_hour, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
                            formatted_data_station[str(parameter)].append([last_hour, ""])
                            # print(last_hour)

                        formatted_data_station[str(parameter)].append([hour, data_stations_response[str(source)][str(station)][str(hour)][str(parameter)]])
                        # print("Else : " + hour)
                        #else:
                            #formatted_data_station[str(parameter)].append([])
                    last_hour = hour # datetime.datetime.strptime(hour, '%Y-%m-%d')
            formatted_data_source[str(station)] = formatted_data_station
        formatted_data[str(source)] = formatted_data_source

    return JsonResponse(json.dumps(formatted_data), safe=False)


def statut(request):
    get_ip(request)
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
    get_ip(request)
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
    get_ip(request)
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
    # Create path for media_path and create path redirect for url
    path_redirect = ''
    path = ''
    for i, p in enumerate(request.GET.getlist('path')):
        path = join(path, p)
        if i==0:
            path_redirect += '?path={}'.format(p)
        else:
            path_redirect += '&path={}'.format(p)

    media_path = join(settings.MEDIA_ROOT, path)
    sources_input = Source.objects.all()
    # Download file if request is passed in POST
    if request.method == 'POST':
        if request.POST.get('filename', '') != '':
            file_path = join(media_path, request.POST.get('filename', ''))
            data_file = open(file_path, 'rb')
            return FileResponse(data_file)
    else:
        folder_tuples = []
        # Iterate over each element of the media path and create tuple (name, True if file else False)
        for e in listdir(media_path):
            if not isfile(join(media_path, e)):
                folder_tuples.append((e,False))
            elif splitext(e)[1] in [".csv", ".txt",".zip"]:
                folder_tuples.append((e,True))

        # Filter the tuples by alphabetical order
        folder_tuples.sort(key=lambda tup: tup[0])

        # Create the path redirect
        if request.GET.get('path', '') == '':
            path_redirect += '?path='
        else:
            path_redirect += '&path='

        originFlavourText = 'Données transformées' if request.GET.get('origin', '') == 'transformed' else 'Données originelles'
        form = DateSelection
        context = {
            'sources_input':sources_input,
            'file': folder_tuples,
            'origin': request.GET.get('origin', ''),
            'origin_flavour': originFlavourText,
            'source': request.GET.get('source', ''),
            'path_redirect': path_redirect,
            'path': path,
            'form': form,
        }
        return render(request, 'manage_data.html', context)


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def harvest_data(request):
    get_ip(request)
    if 'updateOperation' in request.POST and request.POST['updateOperation'] == 'files':
        if 'starting_date' in request.POST and 'ending_date' in request.POST and request.POST['starting_date'] != "" and request.POST['ending_date'] != "":
            source_dict = {
                "climacity": "python3 {}/climacity.py -s {} -e {}".format(settings.CLIMACITY_ROOT, str(request.POST['starting_date']), str(request.POST['ending_date'])),
                "sabra" : "python3 {}/sabra.py -s {} -e {}".format(settings.SABRA_ROOT, str(request.POST['starting_date']), str(request.POST['ending_date'])),
                "vhg" : "python3 {}/vhg.py -s {} -e {}".format(settings.VHG_ROOT, str(request.POST['starting_date']), str(request.POST['ending_date']))
            }
            if 'source_list' in request.POST:
                for s in request.POST.getlist('source_list'):
                    if s in source_dict:
                        print("Launching {}".format(s))
                        print("{}".format(os.system(source_dict[s])))
    elif request.POST['updateOperation'] == 'db':
        print("Updating Database...")
        print("{}".format(os.system("python3 MIDAS/manage.py insert_ssp_db")))
        update_db.insert_stations()
    elif request.POST['updateOperation'] == 'dbInfos':
        print("Updating Databse Informations...")
        print("{}".format(os.system("python3 MIDAS/manage.py update_db_params_infos")))

    return redirect(manage_data)


def about(request):
    get_ip(request)
    return render(request, 'about.html')


def hackathon(request):
    get_ip(request)
    return render(request, 'hackathon.html')


def register(request):
    get_ip(request)
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            request.session['accountCreated'] = True

            return redirect("/")
    else:
        form = RegisterForm()

    return render(request, "registration/registration.html", {"form":form})
