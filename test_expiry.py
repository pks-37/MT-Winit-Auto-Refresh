import requests
import json

from config import BASE_URL, HEADERS, LOGIN_USER

url = f"{BASE_URL}/api/expiry/products"

params = {
    "visitedDate": "2026-07-31",
    "customerCode": "G27",
    "fieldUserCode": "TB1251",
    "loginUserCode": LOGIN_USER
}

r = requests.get(url, params=params, headers=HEADERS)

print(json.dumps(r.json()["data"][0], indent=2))