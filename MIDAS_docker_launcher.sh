#!/bin/sh

echo "Starting"
echo "Install Crontab"
crontab /app/docker/crontab
echo "Start cron service"
service cron start
echo "Making migrations"
python MIDAS/manage.py makemigrations MIDAS_app
echo "Migrating"
python MIDAS/manage.py migrate
echo "Creating super user"
DJANGO_SUPERUSER_USERNAME=$admin_username DJANGO_SUPERUSER_PASSWORD=$admin_password DJANGO_SUPERUSER_EMAIL=$admin_email python3 MIDAS/manage.py createsuperuser --noinput
echo "Runing server"
python MIDAS/manage.py runserver 0.0.0.0:8000 --noreload
