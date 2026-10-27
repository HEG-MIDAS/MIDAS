#!/bin/sh
# Demarrage du devcontainer : dependances, migrations, compte admin, donnees de base, serveur de developpement.
set -e
cd /workspace

echo "==> pip install -r requirements.txt (dans /opt/venv)"
pip install -q -r requirements.txt

echo "==> Migrations"
python MIDAS/manage.py makemigrations MIDAS_app --noinput
python MIDAS/manage.py migrate --noinput

echo "==> Compte admin (${admin_username:-admin})"
DJANGO_SUPERUSER_USERNAME="${admin_username:-admin}" \
DJANGO_SUPERUSER_PASSWORD="${admin_password:-pw}" \
DJANGO_SUPERUSER_EMAIL="${admin_email:-midas@midas.ch}" \
python MIDAS/manage.py createsuperuser --noinput 2>/dev/null || echo "    (existe deja)"

echo "==> Sources / stations / parametres (sources.csv + media/transformed)"
python MIDAS/manage.py insert_ssp_db

echo "==> runserver 0.0.0.0:8000 (port 8282 sur l'hote)"
exec python MIDAS/manage.py runserver 0.0.0.0:8000
