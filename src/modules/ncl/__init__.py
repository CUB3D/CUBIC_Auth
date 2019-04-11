from ...core.module_base import *
import base64
import json

mod_auth = Blueprint('ncl', __name__, url_prefix='/app/ncl/')


@mod_auth.route("featureSuggest", methods=["GET", "POST"])
def add_feature_suggest():
    with Files.get_new_uniq_file("w", prefix="FEAT") as f:
        f.write(base64.urlsafe_b64decode(request.data).decode("UTF-8"))
    return json.dumps({"Status": 0})
