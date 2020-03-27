from flask import Blueprint, redirect, url_for

root = Blueprint("root", __name__)


@root.route("/")
def default():
    return redirect(url_for("login"))
