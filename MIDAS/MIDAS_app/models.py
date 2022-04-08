from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=50)
    email = models.EmailField('Adresse mail', unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)


class Source(models.Model):
    name = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)
    infos = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.name
    

class Station(models.Model):
    name = models.CharField(max_length=255, blank=True)
    infos = models.TextField(max_length=500, blank=True)
    latitude = models.DecimalField(blank=True, max_digits=30, decimal_places=15, null=True)
    longitude = models.DecimalField(blank=True, max_digits=30, decimal_places=15, null=True)
    height = models.DecimalField(blank=True, max_digits=10, decimal_places=5, help_text="Height in meters", null=True)

    def __str__(self):
        return self.name


class Parameter(models.Model):
    name = models.CharField(max_length=255, blank=True)
    infos = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class StationBySource(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, verbose_name="related source")
    station = models.ForeignKey(Station, on_delete=models.CASCADE, verbose_name="related station")


class ParamatersOfStationBySource(models.Model):
    station_by_source = models.ForeignKey(StationBySource, on_delete=models.CASCADE, verbose_name="related station by source")
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, verbose_name="related parameter")
