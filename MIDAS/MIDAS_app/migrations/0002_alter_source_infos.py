# Generated by Django 4.0.3 on 2022-04-08 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MIDAS_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='infos',
            field=models.TextField(blank=True, max_length=500),
        ),
    ]
