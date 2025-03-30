import os
import requests
import subprocess
import threading
import json
from app.config.constants import BASE_URL

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


def run_rathole():
    subprocess.run(["./rathole", "config.toml"], capture_output=True)


def save_certificate(subdomain, fullchain, privkey):
    if not os.path.exists("./certs"):
        os.mkdir("./certs")
    
    path = f"./certs/{subdomain}"
    if not os.path.exists(path):
        os.mkdir(path)
    
    with open(f"{path}/fullchain.pem", "w") as file:
        file.write(fullchain)
    
    with open(f"{path}/privkey.pem", "w") as file:
        file.write(privkey)


def save_token(token):
    with open("secrets.json", "w") as f:
        json.dump({"token": token}, f)


def save_developer_token(developer_token):
    with open("secrets.json", "r") as f:
        conf = json.load(f)

    with open("secrets.json", "w") as f:
        conf["developer_token"] = developer_token

        json.dump(conf, f)
