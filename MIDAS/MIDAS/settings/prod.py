from .base import *
import os

DEBUG=True
LANGUAGE_CODE = 'fr-ch'
STATIC_ROOT=os.path.join(BASE_DIR,'../static')
COMPRESS_ENABLED = True