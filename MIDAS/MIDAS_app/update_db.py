from .models import Source, Station, Parameter, Hash
from django.conf import settings
import os
import hashlib

def update_sources():
    sources_csv_path = os.path.join(settings.BASE_DIR, '../sources.csv')
    if os.path.isfile(sources_csv_path):
        hash_source = Hash.objects.filter(name='Sources')
        sources_csv = open(sources_csv_path, 'r')
        sources_csv_array = sources_csv.read().splitlines()
        hash_object = hashlib.sha256(sources_csv.read().encode())
        hex_dig = hash_object.hexdigest()
        create_sources = False
        if len(hash_source) == 0:
            h = Hash(name='Sources', hash_value=hex_dig)
            h.save()
            create_sources = True
        if create_sources or (len(hash_source) > 0 and hash_source[0].hash_value != hex_dig):
            for source in sources_csv_array[1:]:
                elements = source.split(',')
                if len(Source.objects.filter(name=elements[0])) == 0:
                    s = Source(name=elements[0], url=elements[1], infos=elements[2])
                    s.save()


def update_stations_and_parameters():
    station_transformed_path = os.path.join(settings.MEDIA_ROOT, 'transformed/')
    sources_dir = [f for f in os.listdir(station_transformed_path) if os.path.isdir(os.path.join(station_transformed_path, f))]
    print()
