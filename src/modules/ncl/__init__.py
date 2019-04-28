from src.core.module_base import *
import base64
import json

mod_ncl = Blueprint('ncl', __name__, url_prefix='/app/ncl/')


@mod_ncl.route("featureSuggest", methods=["GET", "POST"])
def add_feature_suggest():
    with Files.get_new_uniq_file("w", prefix="FEAT") as f:
        f.write(base64.urlsafe_b64decode(request.data).decode("UTF-8"))
    return json.dumps({"Status": 0})


@mod_ncl.route("static_config")
def app_ncl_static_config():
    return json.dumps({
        "version": 219,
        "url_arm": "https://cloud.cub3d.pw/index.php/s/XBENdiMkTAFAQN9/download"
    })
