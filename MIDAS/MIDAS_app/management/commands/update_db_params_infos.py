from django.core.management.base import BaseCommand, CommandError
from MIDAS_app.update_db import update_infos_parameters, insert_lat_long_from_csv


class Command(BaseCommand):
    help = 'Create the sources, stations, or parameters in DB if they don\'t already exist'

    def handle(self, *args, **options):
        update_infos_parameters()
        insert_lat_long_from_csv()
