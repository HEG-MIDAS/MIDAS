from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=50)
    email = models.EmailField('Adresse mail', unique=True)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
