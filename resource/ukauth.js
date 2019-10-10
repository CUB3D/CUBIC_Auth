class User {
   constructor(username) {
      this.username = username;
   }
}

class UKAuth {
    constructor() {
        this.appDescription = {};
    }

    init(appDescription) {
        this.appDescription = appDescription;

        document.getElementById("CUBIC_LOGIN").onclick = () => {
            window.location.href = UKAUTH_BASE_URL + "/app/" + this.appDescription.APP_ID + "/auth";
        }

        get(UKAUTH_BASE_URL + "/api/app/" + this.appDescription.APP_ID + "/user/details", (data) => {
            console.log(data);
            ukauth.loginCallback(data);
        });
    }

    onLogin(callback) {
        ukauth.loginCallback = callback;
    }
}

let ukauth = new UKAuth();

let get = (url, callback) => {
   let xhr = new XMLHttpRequest();
   xhr.onload = callback;
   xhr.open("GET", url, true);
   xhr.send();
};

let UKAUTH_BASE_URL = "http://localhost:8081";
