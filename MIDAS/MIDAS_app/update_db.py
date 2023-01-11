from .models import Source, Station, Parameter, ParametersOfStation
from django.conf import settings
import os
import re


header_dictionary = {
    'PM25': 'PM2.5',
    'CS125_Vis': 'Dvis_Avg',
    'Baro': 'Pa_Avg',
}


def insert_sources():
    print("Inserting sources")
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
    print("Inserting stations")
    station_transformed_path = os.path.join(settings.MEDIA_ROOT, 'transformed/')
    sources_dir = [source.name for source in Source.objects.all()]
    for dir in sources_dir:
        working_path = os.path.join(station_transformed_path, dir)
        if os.path.isdir(working_path):
            for station in os.listdir(working_path):
                if os.path.isdir(os.path.join(working_path, station)):
                    station = station.replace(':', ' ')
                    if len(Station.objects.filter(name=station)) == 0:
                        s = Station(name=station, source=Source.objects.get(name=dir))
                        s.save()


def insert_parameters():
    print("Inserting parameters")
    station_transformed_path = os.path.join(settings.MEDIA_ROOT, 'transformed/')
    sources_dir = [source.name for source in Source.objects.all()]
    for dir in sources_dir:
        working_path = os.path.join(station_transformed_path, dir)
        if os.path.isdir(working_path):
            for station in os.listdir(working_path):
                station_path = os.path.join(working_path, station)
                if os.path.isdir(station_path):
                    for file in os.listdir(station_path):
                        if file.split('.')[-1] == 'csv':
                            stationfile = file.split('.')[0].split('_')[1].replace(':', ' ')
                            header = ''
                            with open(os.path.join(station_path, file)) as f:
                                header = f.readline()
                            for parameter in header.split(','):
                                param = parameter.replace('*', '').replace('\n', '')
                                if param not in ['gmt', 'localtime', 'Date [GMT+1]']:
                                    if len(Parameter.objects.filter(name=param)) == 0:
                                        p = Parameter(name=param)
                                        p.save()
                                    if len(ParametersOfStation.objects.filter(name="{}-{}".format(stationfile, param))) == 0:
                                        if len(Station.objects.filter(name=stationfile)) > 0 :
                                            p = ParametersOfStation(station=Station.objects.get(name=stationfile), parameter=Parameter.objects.get(name=param))
                                            p.save()


def update_infos_parameters():
    print("Updating parameters")
    station_original_path = os.path.join(settings.MEDIA_ROOT, 'original/')
    # Get all the sources in the DB (Directories should be called the same)
    sources_dir = [source.name for source in Source.objects.all()]
    # Get all the paramaters and do a list to work with
    parameters = [parameter.name for parameter in Parameter.objects.all()]
    # Check that we have at least one parameter
    if len(parameters) > 0:
        for dir in sources_dir:
            working_path = os.path.join(station_original_path, dir)
            if os.path.isdir(working_path):
                if dir == 'Climacity':
                    for file in os.listdir(working_path):
                        if file.split('.')[-1] == 'csv':
                            with open(os.path.join(working_path, file)) as f:
                                for line in f:
                                    line_array = re.split('\s{3,}', line.rstrip())
                                    if re.match("^-+-$", line.rstrip()):
                                        break
                                    if line_array[0] in parameters:
                                        Parameter.objects.filter(name=line_array[0]).update(infos=line_array[1])
                                        parameters.remove(line_array[0])
                                    if line_array[0] in header_dictionary.keys():
                                        Parameter.objects.filter(name=header_dictionary[line_array[0]]).update(infos=line_array[1])
                                        parameters.remove(header_dictionary[line_array[0]])
                        if len(parameters) <= 0:
                            break
                if dir == 'SABRA':
                    for file in os.listdir(working_path):
                        if file.split('.')[-1] == 'csv' and file.split('_')[-1].split('.')[0] in parameters:
                            with open(os.path.join(working_path, file)) as f:
                                for line in f:
                                    if ' Polluant:  ' in line:
                                        polluant = line.rstrip().split(' Polluant:  ')[1]
                                        Parameter.objects.filter(name=polluant.split('(')[1][:-1]).update(infos=polluant.split('(')[0].replace('  ', ' '))
                                        parameters.remove(polluant.split('(')[1][:-1])
                                    elif line == '\n':
                                        break
                        if len(parameters) <= 0:
                            break
            if len(parameters) <= 0:
                break


# regex detecting 3 or more spaces : \s{3,}
