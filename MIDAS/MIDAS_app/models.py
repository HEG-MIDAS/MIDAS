from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import AbstractUser
import unicodedata
import re

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', str(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

class User(AbstractUser):
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=100)
    email = models.EmailField('Adresse mail', unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)


class Source(models.Model):
    name = models.CharField(max_length=255, blank=True, unique=True)
    slug = models.CharField(max_length=255, blank=True, unique=True, editable=False)
    url = models.URLField(blank=True)
    infos = models.TextField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        self.slug = "{}".format(re.sub(r"[^\w\s]", '_', remove_accents((self.name).lower().replace(' ', '_'))))
        super(Source, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class Station(models.Model):
    name = models.CharField(max_length=255, blank=True, unique=True)
    slug = models.CharField(max_length=255, blank=True, unique=True, editable=False)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, verbose_name='Source of the station', related_name='station')
    infos = models.TextField(max_length=500, blank=True)
    latitude = models.DecimalField(blank=True, max_digits=30, decimal_places=15, null=True)
    longitude = models.DecimalField(blank=True, max_digits=30, decimal_places=15, null=True)
    height = models.DecimalField(blank=True, max_digits=10, decimal_places=5, help_text="Height in meters", null=True)

    def save(self, *args, **kwargs):
        self.slug = "{}".format(re.sub(r"[^\w\s]", '_', remove_accents((self.name).lower().replace(' ', '_'))))
        super(Station, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Parameter(models.Model):
    name = models.CharField(max_length=255, blank=True, unique=True)
    slug = models.CharField(max_length=255, blank=True, unique=True, editable=False)
    infos = models.TextField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        self.slug = "{}".format(re.sub(r"[^\w\s]", '_', remove_accents((self.name).lower().replace(' ', '_'))))
        super(Parameter, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ParamatersOfStation(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, verbose_name="Related station", related_name='paramaters_of_station')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, verbose_name="Related parameter", related_name='paramaters_of_station')

    name = models.CharField(max_length=255, blank=True, unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.name = "{}-{}".format(self.station, self.parameter)
        super(ParamatersOfStation, self).save(*args, **kwargs)

    def __str__(self):
        return  "{}-{}".format(self.station, self.parameter)


class GroupOfFavorite(models.Model):
    name = models.CharField(max_length=255, blank=True, unique=True)
    slug = models.CharField(max_length=255, blank=True, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Related user", blank=False, related_name='group_of_favorite')

    def save(self, *args, **kwargs):
        self.slug = "{}".format(re.sub(r"[^\w\s]", '_', remove_accents((self.name).lower().replace(' ', '_'))))
        super(GroupOfFavorite, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    starting_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    ending_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    paramaters_of_station = models.ManyToManyField(ParamatersOfStation)
    group_of_favorite = models.ForeignKey(GroupOfFavorite, on_delete=models.CASCADE, verbose_name="Related favorite group", related_name='favorite')

    def __str__(self):
        return 'FavOf:{}'.format(self.group_of_favorite)
