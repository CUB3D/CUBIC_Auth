import requests
from urllib.parse import quote
import json
from sys import argv
from pprint import pprint

if len(argv) < 3:
    print("Usage: send_notifciation: [-r <key:value>...] [<title> <message>]")
    exit(1)

json_obj = {}

if "-r" in argv:
    print("Working in raw mode")
    payload = [{"key": x.split(":")[0], "value": x.split(":")[1]} for x in argv[2:]]
    json_obj = {
        "targetAppID": "pw.cub3d.uk",
        "dataPayload": payload
    }
else:
    title = argv[-2]
    content = argv[-1]

    json_obj = {
    "targetAppID": "pw.cub3d.uk",
        "message": {
            "title": title,
            "content": content,
        }
    }


print("Sending:")
pprint(json_obj)
json_string = quote(json.dumps(json_obj)).strip()

print(json_string)

BASE_URL = "https://cbns.cub3d.pw"
BASE_URL = "http://localhost:8090"
print(requests.post(BASE_URL + "/post/device_common/" + json_string))

print(requests.post(BASE_URL + "/device/test/post", json=json_obj))
