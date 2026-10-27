from .base import *
import os

# Debug desactive en production (DJANGO_DEBUG=1 pour le reactiver ponctuellement).
# Sans DEBUG, Django ne sert plus /static/ lui-meme : c'est WhiteNoise (middleware dans base.py) qui le fait.
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
LANGUAGE_CODE = 'fr-ch'
STATIC_ROOT=os.path.join(BASE_DIR,'../static')
COMPRESS_ENABLED = True