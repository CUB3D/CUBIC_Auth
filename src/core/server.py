# -*- coding: future_fstrings -*-
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import make_response
from flask import url_for
from flask_uwsgi_websocket import GeventWebSocket
import functools
import time
import bcrypt
import os
import sqlite3
import base64
import json
from flask_redis import FlaskRedis
import redis
import multiprocessing
import ulid
# TODO: get rid of ulid, change to custom id
# from ..modules.idcarddetect import detect_flask
from urllib.request import urlretrieve
import json
import time
import sys
from ..modules.idcarddetect import detect_flask
from ..modules.ncl import add_feature_suggest


#from ..modules import crashtrak

app = Flask(__name__, template_folder="/home/code/templates/")
websocket = GeventWebSocket(app)
app.config["REDIS_URL"] = "redis://:@localhost:6379/0"

crashtrak = __import__("src.modules.crashtrak", fromlist=["mod_auth"])

app.register_blueprint(crashtrak.mod_auth)

def genUniqueToken():
    return base64.b64encode(os.urandom(64)).decode("utf-8")


@app.route("/app/demo_camera/main")
def app_demo_camera():
    return render_template("demo_camera.html")


@app.route("/app/demo_camera/submit", methods=["POST", "GET"])
def app_demo_camera_submit():
    img = request.form["img"]

    while len(img) % 4 != 0:
        img += "="

    img = img.split(",")[-1]

    with open("test-dump.txt", "w") as f:
        f.write(img)

    imgData = base64.urlsafe_b64decode(img)

    return json.dumps(detect_flask.doFind(imgData))




@websocket.route("/cbns/<deviceToken>")
def test(ws, deviceToken):
    print("Recieved websocket connect")
    print("starting pubsub, channel_device_{}".format(deviceToken))
    redis_store = FlaskRedis(app)
    r = redis_store.pubsub()
    r.subscribe("channel_device_{}".format(deviceToken), "channel_device_common")

    running = True
    while True:
        for msg in r.listen():

            data = msg["data"]

            if type(data) is bytes:
                data = data.decode("utf-8")
            else:
                data = str(data)

            print("Dispatching message:", data)
            ws.send(data)

            print("Checking for messages")
            while True:
                dat = ws.receive()
                if dat is None:
                    running = False
                    print("Got EOS")
                    break
                if dat == b'':
                    break
                print("DAT:", dat)
            print("MSG check done")

        if not running:
            break
    print("Killing ws for", deviceToken)


def verifyLogin():
    if "UK_AUTH_TOKEN" in request.cookies:
        token = request.cookies.get("UK_AUTH_TOKEN")

        with sqlite3.connect("Test.db") as con:
            cur = con.cursor()
            # Validate the auth token
            cur.execute("""SELECT SessionID FROM Session WHERE SessionToken=?""", (token,))

            cur.execute("""Insert INTO SessionAccess (SessionID, AccessTime, Success) VALUES (?, ?, ?)""",
                        (cur.fetchall()[0][0], int(time.time()), 1))
            con.commit()


def setupDB():
    with sqlite3.connect("Test.db") as con:
        cur = con.cursor()

    # Users and sessions
    cur.execute("""CREATE TABLE User (
        UserID INTEGER PRIMARY KEY NOT NULL UNIQUE,
        Username VARCHAR NOT NULL UNIQUE,
        PasswordHash VARCHAR NOT NULL
        );""")
    con.commit()

    cur.execute("""CREATE TABLE Session (
        SessionID INTEGER PRIMARY KEY NOT NULL UNIQUE,
        SessionToken VARCHAR NOT NULL UNIQUE,
        UserID INT NOT NULL,
        FOREIGN KEY(UserID) REFERENCES User(UserID)
        );""")
    con.commit()

    cur.execute("""CREATE TABLE SessionAccess (
        UsageID INTEGER PRIMARY KEY NOT NULL UNIQUE,
        SessionID INTEGER NOT NULL UNIQUE,
        AccessTime INTEGER NOT NULL,
        Success INTEGER NOT NULL,
        FOREIGN KEY(SessionID) REFERENCES Session(SessionID) 
        );""")
    con.commit()

    cur.execute("""CREATE TABLE LoginAttempt (
        AttemptID INTEGER PRIMARY KEY NOT NULL UNIQUE,
        Username VARCHAR NOT NULL,
        AccessTime INTEGER NOT NULL,
        Success INTEGER NOT NULL
        );""")
    con.commit()


    # Applications
    cur.execute("""CREATE TABLE Application (
        ApplicationID INTEGER PRIMARY KEY NOT NULL UNIQUE,
        ApplicationToken VARCHAR NOT NULL,
        CreationTime INTEGER NOT NULL,
        OwnerID INTEGER NOT NULL,
        Description VARCHAR NOT NULL,
        ApplicationName VARCHAR NOT NULL,
        FOREIGN KEY(OwnerID) REFERENCES User(UserID)
        );""")
    con.commit()

    cur.execute("""CREATE TABLE UserApplication (
        UserApplicationID INTEGER PRIMARY KEY NOT NULL UNIQUE,
        UserID INTEGER NOT NULL,
        ApplicationID INTEGER NOT NULL,
        FOREIGN KEY(UserID) REFERENCES User(UserID),
        FOREIGN KEY(ApplicationID) REFERENCES Application(UserApplicationID)
        );""")
    con.commit()

    cur.execute("""CREATE TABLE Device (
        DeviceID INTEGER PRIMARY KEY NOT NULL UNIQUE,
        DeviceToken VARCHAR NOT NULL,
        DeviceType VARCHAR NOT NULL,
        OwnerID INTEGER NOT NULL,
        BatteryPercent INTEGER DEFAULT 0,
        Latitude REAL DEFAULT 0,
        Longitude REAL DEFAULT 0,
        FOREIGN KEY(OwnerID) REFERENCES User(UserID)
        );""")
    con.commit()



@app.route("/")
def default():
    return redirect("/login")


@app.route("/resource/<type>/<file>")
def script(type, file):
    with open(os.path.join("/home/code/resource/", os.path.basename(file)), "r") as f:
        resp = make_response(f.read())
        resp.mimetype = "text/" + type
        return resp


def isLoginValid():
    if "UK_AUTH_TOKEN" in request.cookies:
        token = request.cookies.get("UK_AUTH_TOKEN")

        with sqlite3.connect("Test.db") as con:
            cur = con.cursor()
            cur.execute("""SELECT UserID FROM Session WHERE SessionToken=?""", (token,))

            rows = cur.fetchall()

            if len(rows) > 0:
                return True
            else:
                print("Invalid login token found", token)
    else:
        print("No login token found where required")

        return False

def getCurrentUserDetails():
    #TODO: maybe second token check
    token = request.cookies.get("UK_AUTH_TOKEN")

    with sqlite3.connect("Test.db") as con:
        cur = con.cursor()
        cur.execute("""SELECT Username, User.UserID FROM User INNER JOIN Session ON Session.UserID = User.UserID WHERE SessionToken=?""", (token,))

        username,userID = cur.fetchall()[0]

        return {
            "Username": username,
            "Token": token,
            "UserID": userID
        }


def requireLogin(view):
    @functools.wraps(view)
    def wrapper(**args):
        if isLoginValid():
            return view(**args)
        else:
            print("Page access attempted with invalid login")
            return redirect(url_for("/login"))

    return wrapper


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


@app.route("/settings/developer/newApplication")
@requireLogin
def newApplication():
    applicationName = request.form["appName"]
    applicationDesc = request.form["appDesc"]
    token = genUniqueToken()
    userInfo = getCurrentUserDetails()

    with sqlite3.connect("Test.db") as con:
        cur = con.cursor()
        cur.execute("""INSERT INTO Application (ApplicationToken, CreationTime, OwnerID, Description, ApplicationName) VALUES (?, ?, ?, ?, ?)""",
                    (token, time.clock(), userInfo["UserID"], applicationDesc, applicationName))
        con.commit()

    return redirect("/settings/applications")


@app.route("/auth", methods=["POST", "GET"])
def auth():
    u = request.form["Username"]
    p = request.form["Password"]

    # Get password hash
    with sqlite3.connect("Test.db") as con:
        cur = con.cursor()
        cur.execute("""SELECT PasswordHash,UserID,Username FROM User WHERE Username=? """, (u,))

    rows = cur.fetchall()
    if len(rows) <= 0:
        resp = redirect("/login")
        resp.set_cookie("UK_LOGIN_FAIL", "1")
        return resp

    passwordHash, userID, username = rows[0]

    resp = redirect("/login")

    if bcrypt.checkpw(p.encode("utf-8"), passwordHash.encode("utf-8")):
        # If the login was correct then create and store a session token
        token = base64.b64encode(os.urandom(64)).decode("utf-8")

        with sqlite3.connect("Test.db") as con:
            cur = con.cursor()
            cur.execute("""INSERT INTO Session (SessionToken, UserID) VALUES (?,?)""", (token, userID))
            con.commit()

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

        with sqlite3.connect("Test.db") as con:
            cur = con.cursor()
            cur.execute("""SELECT UserID FROM Session WHERE SessionToken=?""", (token,))

            rows = cur.fetchall()

            if len(rows) > 0:
                return redirect("/loginSuccess")

    # Show error message if login failed before (failed auth cookies present)
    error = ("UK_LOGIN_FAIL" in request.cookies and request.cookies.get("UK_LOGIN_FAIL") == "1")

    # show login template
    resp = make_response(render_template("login.html", authError=1 if error else 0))
    resp.set_cookie("UK_LOGIN_FAIL", "0")

    return resp


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
def api_accoutExists(username):
    with sqlite3.connect("Test.db") as con:
        cur = con.cursor()
        cur.execute("""SELECT Username FROM User WHERE Username=?""", (username,))
        if len(cur.fetchall()) > 0:
            return json.dumps({"Exists": 1})
        else:
            return json.dumps({"Exists": 0})


@app.route("/newDevice/<name>")
@requireLogin
def newDevice(name):
    print("Adding device")
    with sqlite3.connect("Test.db") as con:
        cur = con.cursor()

        token = str(ulid.new()) + str(ulid.new())
        ownerID = getCurrentUserDetails()["UserID"]

        print("Adding device", token, name)

        cur.execute("""INSERT INTO Device (DeviceToken, DeviceType, OwnerID) VALUES (?, ?, ?)""", (token, name, ownerID))
        con.commit()

    resp = make_response()
    resp.set_cookie("UK_DEVICE_TOKEN", token)
    return resp


@app.route("/pingDevice/<token>")
def ping(token):
    redis_store = FlaskRedis(app)
    redis_store.publish("channel_device_{}".format(token), "Ping")
    return "Pinge'd"


@app.route("/api/updateDevice/<token>/<bat>/<lat>/<long>")
def updateDevice(token, bat, lat, long):
    with sqlite3.connect("Test.db") as con:
        cur = con.cursor()

        cur.execute("UPDATE Device SET BatteryPercent=?, Latitude=?, Longitude=? WHERE DeviceToken=?", (bat, lat, long, token))
        con.commit()
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

    with sqlite3.connect("Test.db") as con:
        cur = con.cursor()

        cur.execute("""SELECT Username FROM User WHERE Username=?""", (username,))

        if len(cur.fetchall()) > 0:
            resp = redirect("/register")
            resp.set_cookie("UK_USERNAME_TAKEN", "1")
            return resp

        cur.execute("""INSERT INTO User (Username, PasswordHash) VALUES (?, ?)""",
                    (username, hash))
        con.commit()

    return redirect("/login")


if not os.path.exists("Test.db"):
    setupDB()


def pingDevicesThread():
    """
    Every 10 minutes, ping every known device to see if they are active
    :return:
    """
    r = redis.Redis(host="localhost")
    while True:
        r.publish("channel_device_common", "device_update_status")
        print("Global update done")
        time.sleep(15 * 60)


def start():
    multiprocessing.Process(target=pingDevicesThread).start()
    app.run(host="0.0.0.0", port=8085, gevent=100)

if __name__ == '__main__':
    start()