FROM python:3.9.11-buster

# Update all
RUN apt-get update && apt-get upgrade -y
# Install crontab firefox (for scraper)
RUN apt-get install cron firefox-esr -y

# Copy essential files to docker env
COPY docker /app/docker
COPY Climacity /app/Climacity
COPY backup /app/backup
COPY media /app/media
COPY MIDAS /app/MIDAS
COPY packaging_merge_csv_by_date /app/packaging_merge_csv_by_date
COPY SABRA /app/SABRA
COPY requirements.txt /app/requirements.txt
COPY MIDAS_docker_launcher.sh /app/MIDAS_docker_launcher.sh

# Env
WORKDIR /app
ARG DJANGO_SETTINGS_MODULE=MIDAS.settings.prod
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

# Install requirements
RUN pip3 install -r requirements.txt

# Delete used files
RUN rm requirements.txt
RUN rm -rf packaging_merge_csv_by_date/

EXPOSE 8000

CMD ./MIDAS_docker_launcher.sh
