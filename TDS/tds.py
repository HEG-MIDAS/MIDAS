import time
from hashlib import sha256
from base64 import b64encode
import requests
import json

server = "demo.tetraedrehost.ch"
page = "/io/web_service_json.php"

dossier_id = 49001

username = "test_json@tetraedre.com"
encrypted_password = "ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f" # Plain text "12345678"

metering_code = "AU1"

challenge_txt = str(int(time.time()))
challenge_password = sha256((encrypted_password+challenge_txt).encode('utf-8')).hexdigest()


def get_remote_HTTP_or_HTTPS_page(server, page, content, configuration, verbose=0, timeout=30):
    http_config = {}
    headers = []

    headers.append("Content-type: "+configuration["content_type"])
    http_config["user_agent"] = "tetraedre/TDS"
    http_config["method"] = configuration["method"]

    if len(content) > 0:
        http_config["content"] = content
    else:
        if configuration["method"]=="POST":
            http_config["method"] = "GET"
    
    if len(configuration["username"])>0 or len(configuration["password"])>0:
        headers.append("Authorization: Basic "+b64encode(configuration["username"]+":"+configuration["password"]))
    if len(configuration["token"]) > 0:
        headers.append("token: "+configuration["token"])
    http_config["header"] = {}
    for i, e in enumerate(headers):
        http_config["header"][str(i)] = e

    options = {
        "http": http_config,
    }

    url = "http://"+server+":"+str(configuration["port"])+page
    if configuration["protocol"]=="HTTPS":
        options["ssl"] = {
                    "verify_peer": False,
                    "verify_peer_name": False,
        }
        
        url = "https://"+server+":"+str(configuration["port"])+page

    print("------------------------Options------------------------")
    print(json.dumps(options))

    r = requests.post(url, data=json.dumps(options))
    print("------------------------Response------------------------")
    print(str(r)+"\n"+str(r.headers)+"\n"+str(r.content))

    


def my_HTTP_post_json(server, page, content, username="", password="", port=80, timeout=30, verbose=0):
    connection_info = {
        "method": "POST",
        "token": "",
        "content_type": "application/json",
        "port": port,
        "username": username,
        "password": password,
        "protocol": "HTTPS",
        "port": 443,
    }

    reponse = get_remote_HTTP_or_HTTPS_page(server, page, content, connection_info)


def check_access():
    parameters = {
        "operation": "check_access",
        "username": username,
        "challenge": challenge_txt,
        "dossier_id": dossier_id,
        "challenge_password": challenge_password,
    }


    print("Parameters : \n")
    print(parameters)

    my_HTTP_post_json(server, page, parameters)


def ping():
    parameters = {
        "operation": "ping"
    }

    my_HTTP_post_json(server, page, parameters)

ping()
