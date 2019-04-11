from ...core.module_base import *
import base64
import json

mod_auth = Blueprint('crashtrak', __name__, url_prefix='/app/delitics/')


@mod_auth.route("submit", methods=["GET", "POST"])
def add_delitics_sub():
    with Files.get_new_uniq_file("w", prefix="CT") as f:
        f.write(base64.urlsafe_b64decode(request.data).decode("UTF-8"))
    return json.dumps({"Status": 0})
