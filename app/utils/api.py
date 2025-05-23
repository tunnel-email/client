import requests
import webbrowser
from app.config.constants import BASE_URL, BASE_DOMAIN
import os
import sys


def yandex_login(token):
    url = f"{BASE_URL}/auth/yandex/login?token={token}"
    webbrowser.open(url)

def get_ttl(tunnel_id):
    req = requests.get(f"{BASE_URL}/tunnel_status", params={"tunnel_id": tunnel_id}).json()
    return req["ttl"]

def check_security(subdomain):
    req = requests.get(f"https://crt.sh/?q={subdomain}&output=json").json()

    return req

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        # pyinstaller
        base_path = sys._MEIPASS
    elif "__compiled__" in globals():
        # nuitka
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        # python script
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    return os.path.join(base_path, relative_path)


def script_path(relative_path):
    if getattr(sys, 'frozen', False):
        # pyinstaller
        base_path = os.path.dirname(sys.executable)
    elif "__compiled__" in globals():
        # nuitka
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        # если python скрипт
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    return os.path.join(base_path, relative_path)
    