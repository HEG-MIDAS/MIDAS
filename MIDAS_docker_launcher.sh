#!/bin/sh

echo "Starting"
echo "Making migrations"
python MIDAS/manage.py makemigrations MIDAS_app --noinput
echo "Migrating"
python MIDAS/manage.py migrate --noinput
echo "Collect Static Files"
python MIDAS/manage.py collectstatic --noinput
echo "Creating super user"
DJANGO_SUPERUSER_USERNAME=$admin_username DJANGO_SUPERUSER_PASSWORD=$admin_password DJANGO_SUPERUSER_EMAIL=$admin_email python MIDAS/manage.py createsuperuser --noinput || echo "Super user already exists"
echo "Running compression module (Closure Compiler)"
python MIDAS/manage.py compress --force
echo "Running server"
python -u MIDAS/manage.py runserver 0.0.0.0:8000 --noreload
