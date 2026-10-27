# Devcontainer MIDAS : Python 3.13 (image devcontainers, utilisateur vscode uid 1000 = coder)
FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

ARG GECKODRIVER_VERSION=0.37.1

# Firefox ESR + geckodriver : scraper SABRA (Selenium) ; zip : archives (zip-folder.sh) ; sqlite3 : inspection de db.sqlite3
# Le depot Yarn livre avec l'image a une cle expiree : on le retire avant apt-get update
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends firefox-esr zip sqlite3 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN case "$(dpkg --print-architecture)" in \
         amd64) GD_ARCH=linux64 ;; \
         arm64) GD_ARCH=linux-aarch64 ;; \
         *) echo "Architecture non geree pour geckodriver" && exit 1 ;; \
       esac \
    && curl -fsSL "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-${GD_ARCH}.tar.gz" \
       | tar -xz -C /usr/local/bin \
    && chmod +x /usr/local/bin/geckodriver

# venv dedie, monte sur un volume nomme par docker-compose.yml ; rempli par dev-start.sh (pip install -r requirements.txt)
RUN python -m venv /opt/venv && chown -R vscode:vscode /opt/venv
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /workspace
USER vscode
