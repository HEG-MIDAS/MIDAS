FROM python:3.9.11-buster

# Update all
RUN apt-get update && apt-get upgrade -y
# Install crontab firefox (for scraper)
RUN apt-get install cron firefox-esr -y

# Copy essential files to docker env
## Docker Env
COPY docker /app/docker
## Python Env
COPY requirements.txt /app/requirements.txt
COPY MIDAS_docker_launcher.sh /app/MIDAS_docker_launcher.sh
## Scraper
COPY Climacity /app/Climacity
COPY SABRA /app/SABRA
COPY logs /app/logs
## Django App
COPY MIDAS /app/MIDAS
COPY static /app/static
COPY media /app/media

# Root Directory
WORKDIR /app
# Env variables
ARG DJANGO_SETTINGS_MODULE=MIDAS.settings.prod
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

# Install requirements
RUN pip3 install -r requirements.txt

# Delete used files
RUN rm requirements.txt
RUN rm -rf packaging_merge_csv_by_date/

# Expose the port for Django
EXPOSE 8000

CMD ./MIDAS_docker_launcher.sh
