from flask import Flask, request, render_template, redirect, make_response, url_for
import functools
import time
import bcrypt
import os
import secrets
import sqlite3
import base64
import multiprocessing
import json
#from src.modules.idcarddetect import detect_flask
import src.database
from src.database import db
from src.models.User import User
from src.models.Session import Session
from src.models.Device import Device
from src.models.SessionAccess import SessionAccess
from src.models.LocationHistory import LocationHistory
from src.models.Application import Application
from src.models.UserApplication import UserApplication

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), "templates/"))
app.config.from_envvar('APP_CONFIG')

src.database.init(app)

crashtrak = __import__("src.modules.crashtrak", fromlist=["mod_auth"])
ncl = __import__("src.modules.ncl", fromlist=["mod_auth"])

app.register_blueprint(crashtrak.mod_auth)
app.register_blueprint(ncl.mod_ncl)


def gen_unique_token(length=32):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    return "".join([secrets.choice(alphabet) for _ in range(length)])


@app.route("/app/demo_camera/main")
def app_demo_camera():
    return render_template("demo_camera.html")


# @app.route("/app/demo_camera/submit", methods=["POST", "GET"])
# def app_demo_camera_submit():
#     img = request.form["img"]
#
#     while len(img) % 4 != 0:
#         img += "="
#
#     img = img.split(",")[-1]
#
#     with open("test-dump.txt", "w") as f:
#         f.write(img)
#
#     imgData = base64.urlsafe_b64decode(img)
#
#     return json.dumps(detect_flask.doFind(imgData))


@app.route("/")
def default():
    return redirect("/login")


@app.route("/resource/<type>/<file>")
def script(type, file):
    with open(os.path.join(os.getcwd(), "resource/", os.path.basename(file)), "r") as f:
        resp = make_response(f.read())
        resp.mimetype = "text/" + type
        return resp


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


    #TODO: Maybe just return user obj
    user = User.query.filter(User.UserID == session.UserID).first()

    if user is not None:
        username = user.Username
        userID = user.UserID

        return {
            "Username": username,
            "Token": token,
            "UserID": userID
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


@app.route("/app/<token>/auth")
def appLogin(token):
    application = Application.query.filter(Application.ApplicationToken == token).first()
    user = getCurrentUserDetails()

    # If the id is invalid then redirect to login page
    if application is None:
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
        # instantly redirect back
        return redirect("//" + application.url + "/" + userApp.Token)

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
    applicationUrl = request.form["redirect-url"]
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

        resp = redirect("/loginSuccess")
        resp.set_cookie("UK_AUTH_TOKEN", token)
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
    ownerID = getCurrentUserDetails()["UserID"]

    print("Adding device", token, name)

    Device(token, name, ownerID).create()

    resp = make_response()
    resp.set_cookie("UK_DEVICE_TOKEN", token)
    return resp


@app.route("/api/updateDevice/<token>/<bat>/<lat>/<long>")
def updateDevice(token, bat, lat, long):
    # Get the device
    device = Device.query.filter(Device.DeviceToken == token).first()

    if device is not None:
        # Store the old location for history
        LocationHistory(device.DeviceID, device.Latitude, device.Longitude).create()

        device.BatteryPercent = bat
        device.Latitude = lat
        device.Longitude = long
        db.session.commit()

    return ""


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
    # multiprocessing.Process(target=pingDevicesThread).start()
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == '__main__':
    start()
