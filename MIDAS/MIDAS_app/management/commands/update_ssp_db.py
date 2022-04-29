from django.core.management.base import BaseCommand, CommandError
from MIDAS_app.update_db import *


class Command(BaseCommand):
    help = 'Create the sources, stations, or parameters in DB if they don\'t already exist'

    def handle(self, *args, **options):
        insert_sources()
        insert_stations()
        insert_parameters()
