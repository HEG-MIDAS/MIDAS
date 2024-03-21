#!/bin/sh

echo "Starting"
# echo "Install Crontab"
# crontab /app/docker/crontab
# echo "Start cron service"
# service cron start
echo "Making migrations"
python MIDAS/manage.py makemigrations MIDAS_app
echo "Migrating"
python MIDAS/manage.py migrate
echo "Collect Static Files"
python MIDAS/manage.py collectstatic --noinput
echo "Creating super user"
DJANGO_SUPERUSER_USERNAME=$admin_username DJANGO_SUPERUSER_PASSWORD=$admin_password DJANGO_SUPERUSER_EMAIL=$admin_email python3 MIDAS/manage.py createsuperuser --noinput
echo "Installing npm"
curl -qL https://www.npmjs.com/install.sh | sh
echo "Installing google-closure-compiler"
npm i -g google-closure-compiler
echo "Runing compression module"
python3 MIDAS/manage.py compress --force
echo "Runing server"
python -u MIDAS/manage.py runserver 0.0.0.0:8000 --noreload
