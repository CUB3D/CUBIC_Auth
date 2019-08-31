import requests
from urllib.parse import quote
import json
from sys import argv

if len(argv) < 3:
    print("Usage: send_notifciation: <title> <message>")
    exit(1)

title = argv[-2]
content = argv[-1]

json_string = quote(json.dumps({
    "targetAppID": "pw.cub3d.uk",
    "message": {
        "title": title,
        "content": content,
    }
}).strip())

print(json_string)

print(requests.post("https://cbns.cub3d.pw/post/device_common/" + json_string))
