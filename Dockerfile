# Image de production MIDAS / GExplore : application Django + scrapers (Climacity, SABRA, VHG)
FROM python:3.13-slim-bookworm

ARG GECKODRIVER_VERSION=0.37.1
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Firefox ESR + geckodriver : scraper SABRA (Selenium) ; zip : archives (zip-folder.sh)
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends firefox-esr zip curl ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN case "$(dpkg --print-architecture)" in \
         amd64) GD_ARCH=linux64 ;; \
         arm64) GD_ARCH=linux-aarch64 ;; \
         *) echo "Architecture non geree pour geckodriver" && exit 1 ;; \
       esac \
    && curl -fsSL "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-${GD_ARCH}.tar.gz" \
       | tar -xz -C /usr/local/bin \
    && chmod +x /usr/local/bin/geckodriver

# Node.js + Google Closure Compiler (filtre JS de django-compressor), installes au build : plus de nvm/npm au demarrage
COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
COPY --from=node:22-bookworm-slim /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && npm install -g google-closure-compiler \
    && npm cache clean --force

WORKDIR /app

# Dependances Python (couche separee : pas reinstallees a chaque changement de code)
COPY requirements.txt /app/requirements.txt
COPY packaging_merge_csv_by_date /app/packaging_merge_csv_by_date
RUN pip install -r requirements.txt \
    && rm -rf requirements.txt packaging_merge_csv_by_date

## Docker Env
COPY docker /app/docker
COPY MIDAS_docker_launcher.sh /app/MIDAS_docker_launcher.sh
## Scrapers
COPY Climacity /app/Climacity
COPY SABRA /app/SABRA
COPY VHG /app/VHG
COPY logs /app/logs
## Django App
COPY MIDAS /app/MIDAS
COPY static /app/static
COPY media /app/media
## DB Update Default value
COPY sources.csv stations_coordinates.csv /app/
## Scheduled scripts (sources.py : recolte quotidienne ; zip-folder.sh : archives)
COPY sources.py zip-folder.sh /app/

# Env variables
ARG DJANGO_SETTINGS_MODULE=MIDAS.settings.prod
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

# Expose the port for Django
EXPOSE 8000

CMD ["./MIDAS_docker_launcher.sh"]
