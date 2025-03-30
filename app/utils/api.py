import requests
import webbrowser
from app.config.constants import BASE_URL, BASE_DOMAIN

def yandex_login(token):
    url = f"{BASE_URL}/auth/yandex/login?token={token}"
    webbrowser.open(url)

def get_ttl(tunnel_id):
    req = requests.get(f"{BASE_URL}/tunnel_status", params={"tunnel_id": tunnel_id}).json()
    return req["ttl"]

def check_security(subdomain):
    req = requests.get(f"https://crt.sh/?q={subdomain}&output=json").json()

    return req