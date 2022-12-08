import time
from hashlib import sha256
from base64 import b64encode
import requests
import json
# DO NOT FORGET TO CREATE env.py FILE WITH
# env_username = with username
# env_encrypted_password = with encrypted password
from env import *

server = "vhg.ch"
page = "/io/web_service_json.php"

dossier_id = 50955

username = env_username
encrypted_password = env_encrypted_password

metering_code = "AU1"

challenge_txt = str(int(time.time()))
challenge_password = sha256((encrypted_password+challenge_txt).encode('utf-8')).hexdigest()

url = "https://"+server+":"+str(443)+page

headers = {
    "Content-Type": "application/json",
    "user_agent": "tetraedre/TDS",
    "method": "POST",
}
data = {
    "operation": "check_access",
    "username": username,
    "challenge": challenge_txt,
    "dossier_id": dossier_id,
    "challenge_password": challenge_password
}

r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
print("------------------------Response------------------------")
print(str(r)+"\n"+str(r.headers)+"\n"+str(r.content))