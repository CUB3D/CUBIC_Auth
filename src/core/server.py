import base64
import functools
import json
import os

import bcrypt
import requests
from authlib.jose import jwt
from flask import Flask, request, render_template, redirect, make_response, url_for

import src.database
from src.database import db
from src.models.Application import Application
from src.models.Device import Device
from src.models.Session import Session
from src.models.SessionAccess import SessionAccess
from src.models.User import User
from src.models.UserApplication import UserApplication

from src.endpoint.root import root
from src.endpoint.clientjs import clientjs

app = Flask(__name__,
            template_folder=os.path.join(os.getcwd(), "templates/"),
            static_url_path="/static",
            static_folder=os.path.join(os.getcwd(), "static")
            )

app.config.from_envvar('APP_CONFIG', silent=True)
app.register_blueprint(root)
app.register_blueprint(clientjs)

SECURE_COOKIES = os.environ["SECURE_COOKIES"] or app.config["SECURE_COOKIES"]
COOKIE_DOMAIN = os.environ["COOKIE_DOMAIN"] or app.config["COOKIE_DOMAIN"]


src.database.init(app)


def is_login_valid():
    if "UK_AUTH_TOKEN" in request.cookies:
        token = request.cookies.get("UK_AUTH_TOKEN")

        user_session = Session.query.filter(Session.SessionToken == token).first()

        if user_session is not None:
            # Log an attempt to use a session
            SessionAccess(user_session.SessionID, 1).create()
            return True
        else:
            print("Invalid login token found", token)
    else:
        print("No login token found for field with required auth")

    return False


def getCurrentUserDetails():
    #TODO: maybe second token check
    token = request.cookies.get("UK_AUTH_TOKEN")

    session = Session.query.filter(Session.SessionToken == token).first()

    # check that the user is logged in
    if session is None:
        return None


    #TODO: Maybe just return user obj
    user = User.query.filter(User.UserID == session.UserID).first()

    if user is not None:
        username = user.Username
        userID = user.UserID
        channel = user.communication_channel

        return {
            "Username": username,
            "Token": token,
            "UserID": userID,
            "Channel": channel
        }


def requireLogin(view):
    @functools.wraps(view)
    def wrapper(**args):
        if is_login_valid():
            return view(**args)
        else:
            print("Page access attempted with invalid login")
            resp = make_response(redirect(url_for("login")))
            resp.set_cookie("UK_AUTH_TOKEN", "")
            return resp

    return wrapper


@app.route("/app/user/<token>")
def app_user_details(token):
    """
    Return the detail of a user for a given user application token, this allows the client to access the users details for use in their app
    :param token: The UserApplication token
    :return: User details, and the token for convenience
    """
    userApp = UserApplication.query.filter(UserApplication.Token == token).first()

    if userApp is None:
        return None

    user = User.query.filter(User.UserID == userApp.UserID).first()

    if user is None:
        return None

    return json.dumps({
        "Name": user.Username,
        "Token": token
    })


@app.route("/app/<token>/<callbackId>/auth")
def appLogin(token, callbackId):
    application = Application.query.filter(Application.ApplicationToken == token).first()
    user = getCurrentUserDetails()
    if user is None:
        print("Invalid user, requesting login")
        return redirect(url_for("login"))

    # If the id is invalid then redirect to login page
    if application is None:
        print("Invalid application, requesting login")
        return redirect(url_for("login"))

    # Has the user already authed the service
    userApp = UserApplication.query.filter((UserApplication.UserID == user["UserID"]) & (UserApplication.ApplicationID == application.ApplicationID)).first()

    if userApp is None:
        print("Redirecting to app auth for " + token)
        # Show a login accept page
        return render_template("application_auth.html",
                               app_name=application.ApplicationName,
                               app_desc=application.Description,
                               app_token=token
                               )
    else:
        print("User has already accepted application " + token)
        # If the user has already accepted the application then send them the token as a notification

        header = {'alg': 'RS256'}
        payload = {
            'username': user['Username'],
            'userId': user['UserID']
        }

        with open("private.pem") as f:
            key = f.read()
        s = jwt.encode(header, payload, key)

        print("Sending reply to", callbackId)

        res = requests.post("https://cbns.cub3d.pw/device/" + callbackId + "/post", json = {
            "targetAppID": "pw.cub3d.uk",
            "dataPayload": [
                {
                    "key": "user_app_id",
                    "value": userApp.Token
                },
                {
                    "key": "JWT",
                    "value": s.decode("utf-8")
                }
            ]
        })

        print("Response:")
        print(res)

        return render_template("app_auth.html")

        # instantly redirect back
        # return redirect("//" + application.url + "/" + userApp.Token)

    #if it is not, check if the current user has accepted it before, if not show a accept page
    #if they have then direct back with a token

    #if not redirect back without login also if no on accept page

@app.route("/app/<token>/reject")
def app_reject(token):
    application = Application.query.filter(Application.ApplicationToken == token).first()

    # If the id is invalid then redirect to login page
    if application is None:
        return redirect(url_for("login"))

    #TODO: add rejection url
    return redirect(application.url)


@app.route("/api/web/locate-device/<id>")
@requireLogin
def api_web_locate_device(id):
    device = Device.query.filter(Device.DeviceID == id).first()
    res = requests.post("https://cbns.cub3d.pw/device/" + device.DeviceToken + "/post", json = {
        "targetAppID": "pw.cub3d.uk",
        "dataPayload": [
            {
                "key": "action",
                "value": "RING_START"
            },
        ]
    })


@app.route("/api/web/stop-locate-device/<id>")
@requireLogin
def api_web_stop_locate_device(id):
    device = Device.query.filter(Device.DeviceID == id).first()
    res = requests.post("https://cbns.cub3d.pw/device/" + device.DeviceToken + "/post", json = {
        "targetAppID": "pw.cub3d.uk",
        "dataPayload": [
            {
                "key": "action",
                "value": "RING_STOP"
            },
        ]
    })


@app.route("/api/web/delete-device/")
@requireLogin
def api_web_remove_device(id):
    device = Device.query.filter(Device.DeviceID == id).first()

from src.utils.token_generator import gen_unique_token


@app.route("/app/<token>/accept")
def app_accept(token):
    """
    If the user accepts a sso request then take then to this page, we will note that they have given permission and then
    give the app a special token to use to get the users details
    :param token: The application token
    :return:
    """
    application = Application.query.filter(Application.ApplicationToken == token).first()

    user = getCurrentUserDetails()

    user_app_token = gen_unique_token()
    UserApplication(user["UserID"], application.ApplicationID, user_app_token).create()

    # If the id is invalid then redirect to login page
    if application is None or user is None:
        return redirect(url_for("login"))

    return redirect("//" + application.url + "/" + user_app_token)


@app.route("/settings/profile")
@requireLogin
def settings():
    username = getCurrentUserDetails()["Username"]

    return render_template("profile.html", username=username)


@app.route("/settings/applications")
@requireLogin
def applications():
    return render_template("applications.html")

@app.route("/settings/devices")
@requireLogin
def settings_devices():
    userId = getCurrentUserDetails()["UserID"]
    devices = Device.query.filter(Device.OwnerID == userId)
    return render_template("settings_devices.html", devices=devices)

@app.route("/settings/developer")
@requireLogin
def developer():
    """
    The developer page, allows creating applications for other systems
    :return:
    """
    return render_template("developer.html")


@app.route("/settings/developer/newApplication", methods=["GET", "POST"])
@requireLogin
def newApplication():
    applicationName = request.form["appName"]
    applicationDesc = request.form["appDesc"]
    applicationUrl = request.form["redirectUrl"]
    token = gen_unique_token()
    userInfo = getCurrentUserDetails()

    Application(token, userInfo["UserID"], applicationDesc, applicationName, applicationUrl).create()

    return render_template("application_create.html", appID=token)


@app.route("/auth", methods=["POST", "GET"])
def auth():
    u = request.form["Username"]
    p = request.form["Password"]

    user = User.query.filter(User.Username == u).first()

    if user is None:
        print("Auth request failed")
        resp = redirect("/login")
        resp.set_cookie("UK_LOGIN_FAIL", "1")
        return resp

    # passwordHash, userID, username = rows[0]

    passwordHash = user.PasswordHash
    userID = user.UserID
    username = user.Username

    resp = redirect("/login")

    if bcrypt.checkpw(p.encode("utf-8"), passwordHash.encode("utf-8")):
        # If the login was correct then create and store a session token
        token = base64.b64encode(os.urandom(64)).decode("utf-8")

        Session(token, userID).create()

        print("Request succeded")

        resp = redirect("/loginSuccess")
        resp.set_cookie(key="UK_AUTH_TOKEN", value=token, max_age=60 * 60 * 72, domain=COOKIE_DOMAIN, secure=SECURE_COOKIES, httponly=True)
        resp.set_cookie("UK_USERNAME", username)
    else:
        resp.set_cookie("UK_LOGIN_FAIL", "1")
    return resp


@app.route("/login")
def login():
    if "UK_AUTH_TOKEN" in request.cookies:
        token = request.cookies.get("UK_AUTH_TOKEN")

        user = Session.query.filter(Session.SessionToken == token).first()

        if user is not None:
            return redirect("/loginSuccess")

    # Show error message if login failed before (failed auth cookies present)
    error = ("UK_LOGIN_FAIL" in request.cookies and request.cookies.get("UK_LOGIN_FAIL") == "1")

    # show login template
    resp = make_response(render_template("login.html", authError=1 if error else 0))
    resp.set_cookie("UK_LOGIN_FAIL", "0")

    return resp


@app.route("/logout")
@requireLogin
def logout():
    token = request.cookies.get("UK_AUTH_TOKEN")

    c = Session.query.filter(Session.SessionToken == token).first()
    db.session.delete(c)
    db.session.commit()
    return redirect("/login")


@app.route("/loginSuccess")
@requireLogin
def loginSuccess():
    username = getCurrentUserDetails()["Username"]
    return render_template("loginSuccess.html", username=username)


@app.route("/register")
def register():
    passwordsDiffer = ("UK_PASSWORDS_DIFFER" in request.cookies and request.cookies.get("UK_PASSWORDS_DIFFER") == "1")
    usernameTaken = ("UK_USERNAME_TAKEN" in request.cookies and request.cookies.get("UK_USERNAME_TAKEN") == "1")

    resp = make_response(render_template("register.html", api_url="/api/accountExists",
                                         passwordsDiffer=passwordsDiffer,
                                         usernameTaken=usernameTaken))
    resp.set_cookie("UK_PASSWORDS_DIFFER", "0")
    resp.set_cookie("UK_USERNAME_TAKEN", "0")
    return resp


@app.route("/api/accountExists/<username>")
def api_account_exists(username):
    user = User.query.filter(User.Username == username).first()
    if user is None:
        return json.dumps({"Exists": 0})
    else:
        return json.dumps({"Exists": 1})


@app.route("/newDevice/<name>")
@requireLogin
def newDevice(name):
    token = gen_unique_token()
    user = getCurrentUserDetails()
    ownerID = user["UserID"]
    channel = user["Channel"]

    print("Adding device", token, name)

    Device(token, name, ownerID).create()

    resp = make_response()
    resp.set_cookie("UK_DEVICE_TOKEN", token)
    resp.set_cookie("UK_CHANNEL", channel)
    return resp


@app.route("/newAccount", methods=["POST", "GET"])
def newAccount():
    username = request.form["Username"]
    password1 = request.form["Password1"]
    password2 = request.form["Password2"]

    # Passwords must be the same
    if password1 != password2:
        resp = redirect("/register")
        resp.set_cookie("UK_PASSWORDS_DIFFER", "1")
        return resp

    # Hash and salt password
    hash = bcrypt.hashpw(password1.encode("utf-8"), bcrypt.gensalt(15)).decode("utf-8")
    # Clear fields
    del password1
    del password2

    user = User.query.filter(User.Username == username).first()

    if user is not None:
            resp = redirect("/register")
            resp.set_cookie("UK_USERNAME_TAKEN", "1")
            return resp
    else:
        User(username, hash).create()

    return redirect("/login")


def start():
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == '__main__':
    start()
