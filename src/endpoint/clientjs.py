from flask import Blueprint, make_response, current_app
import os
from src.core.config import get_app_base_url

clientjs = Blueprint("clientjs", __name__)


@clientjs.route("/ukauth.js")
def resource_client_js():
    with open(os.path.join(os.getcwd(), "static/ukauth.js"), "r") as f:
        content = f.read().replace("{HOST_URL}", get_app_base_url(current_app))
        resp = make_response(content)
        resp.mimetype = "text/javascript"
        return resp
