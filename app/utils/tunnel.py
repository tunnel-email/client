import os
import requests
import subprocess
import threading
import json
import sys
from app.config.constants import BASE_URL, BASE_DOMAIN
from app.utils.api import resource_path, script_path


def create_tunnel(token):
    req = requests.post(f"{BASE_URL}/create_tunnel", json={"token": token})
    
    if req.status_code == 409:
        raise Exception("Туннель уже был создан")
    elif req.status_code == 403:
        raise Exception("Доступ запрещен. Вы указали неверный токен")
    elif req.status_code != 200:
        raise Exception("Что-то пошло не так...")
    
    req_json = req.json()
    
    return (req_json["subdomain"], req_json["tunnel_id"], req_json["tunnel_secret"])

def delete_tunnel(token):
    req = requests.post(f"{BASE_URL}/delete_tunnel", json={"token": token})

    if req.status_code != 200:
        raise Exception("Не удалось удалить почту")


def add_tunnel_to_rathole(tunnel_id, tunnel_secret):
    with open(script_path(".config.toml"), "w") as file:
        file.write(f"""[client]
remote_addr = "{BASE_DOMAIN}:6789"

[client.services.{tunnel_id}]
token = \"{tunnel_secret}\"
local_addr = \"127.0.0.1:8025\"""")



class Rathole:
    def __init__(self):
        self.rh_process = None


    def run(self):
        if sys.platform == "win32":
            rh_path = os.path.join(resource_path("bin"), "rathole.exe")
        else:
            rh_path = os.path.join(resource_path("bin"), "rathole")

        with open(script_path(".rathole.log"), "a") as f:
            self.rh_process = subprocess.Popen([rh_path, script_path(".config.toml")],
                                               stdout=f, stderr=subprocess.STDOUT,
                                               creationflags=subprocess.CREATE_NO_WINDOW)


    def stop(self):
        if self.rh_process:
            try:
                self.rh_process.terminate()
                self.rh_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.rh_process.kill()

            self.rh_process = None



def save_certificate(subdomain, fullchain, privkey):
    certs_path = script_path(".certs")

    if not os.path.exists(certs_path):
        os.mkdir(certs_path)
    
    path = os.path.join(certs_path, subdomain)
    if not os.path.exists(path):
        os.mkdir(path)
    
    with open(os.path.join(path, "fullchain.pem"), "w") as file:
        file.write(fullchain)
    
    with open(os.path.join(path, "privkey.pem"), "w") as file:
        file.write(privkey)


def save_token(token):
    secrets_path = script_path(".secrets.json")

    with open(secrets_path, "w") as f:
        json.dump({"token": token}, f)


def load_secrets():
    secrets_path = script_path(".secrets.json")

    with open(secrets_path, "r") as f:
        data = json.load(f)

        return (data.get("token"), data.get("developer_token"))


def save_developer_token(developer_token):
    secrets_path = script_path(".secrets.json")

    with open(secrets_path, "r") as f:
        conf = json.load(f)

    with open(secrets_path, "w") as f:
        conf["developer_token"] = developer_token

        json.dump(conf, f)
