FROM python:3.9.11-buster

# Update all
RUN apt-get update && apt-get upgrade -y

# Copy essential files to docker env
COPY Climacity /app/Climacity
COPY media /app/media
COPY backup /app/backup
COPY MIDAS /app/MIDAS
COPY packaging_merge_csv_by_date /app/packaging_merge_csv_by_date
COPY SABRA /app/SABRA
COPY requirements.txt /app/requirements.txt
COPY MIDAS_docker_launcher.sh /app/MIDAS_docker_launcher.sh

WORKDIR /app

# Install requirements
RUN pip3 install -r requirements.txt

# Delete used files
RUN rm requirements.txt
RUN rm -rf packaging_merge_csv_by_date/

EXPOSE 8000

CMD ./MIDAS_docker_launcher.sh