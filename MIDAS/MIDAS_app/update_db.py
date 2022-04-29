from .models import Source, Station, Parameter, ParametersOfStation
from django.conf import settings
import os


def insert_sources():
    print("updating sources")
    sources_csv_path = os.path.join(settings.BASE_DIR, '../sources.csv')
    if os.path.isfile(sources_csv_path):
        sources_csv = open(sources_csv_path, 'r')
        sources_csv_array = sources_csv.read().splitlines()
        for source in sources_csv_array[1:]:
            elements = source.split(',')
            if len(Source.objects.filter(name=elements[0])) == 0:
                s = Source(name=elements[0], url=elements[1], infos=elements[2])
                s.save()
        
        sources_csv.close()


def insert_stations():
    print("updating stations")
    station_transformed_path = os.path.join(settings.MEDIA_ROOT, 'transformed/')
    sources_dir = [source.name for source in Source.objects.all()]
    for dir in sources_dir:
        working_path = os.path.join(station_transformed_path, dir)
        if os.path.isdir(working_path):
            for file in os.listdir(working_path):
                if file.split('.')[-1] == 'csv':
                    station = file.split('_')[0]
                    if len(Station.objects.filter(name=station)) == 0:
                        s = Station(name=station, source=Source.objects.get(name=dir))
                        s.save()


def insert_parameters():
    print("updating parameters")
    station_transformed_path = os.path.join(settings.MEDIA_ROOT, 'transformed/')
    sources_dir = [source.name for source in Source.objects.all()]
    for dir in sources_dir:
        working_path = os.path.join(station_transformed_path, dir)
        if os.path.isdir(working_path):
            for file in os.listdir(working_path):
                if file.split('.')[-1] == 'csv':
                    station = file.split('_')[0]
                    header = ''
                    with open(os.path.join(working_path, file)) as f:
                        header = f.readline()
                    for parameter in header.split(','):
                        param = parameter.replace('*', '').replace('\n', '')
                        if param not in ['gmt', 'localtime']:
                            if len(Parameter.objects.filter(name=param)) == 0:
                                p = Parameter(name=param)
                                p.save()
                            if len(ParametersOfStation.objects.filter(name="{}-{}".format(station, param))) == 0:
                                if len(Station.objects.filter(name=station)) > 0 :
                                    p = ParametersOfStation(station=Station.objects.get(name=station), parameter=Parameter.objects.get(name=param))
                                    p.save()
