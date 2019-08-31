class User {
   constructor(username) {
      this.username = username;
   }
}

let get = (url, callback) => {
   let xhr = new XMLHttpRequest();
   xhr.onload = callback;
   xhr.open("GET", url, true);
   xhr.send();
};

let UKAUTH_BASE_URL = "http://localhost:8081";

let ukauth = {
   init: (appDescription) => {
      ukauth.appDescription = appDescription;
      get(UKAUTH_BASE_URL + "/api/app/" + ukauth.appDescription.APP_ID + "/user/details", (data) => {
         console.log(data);
         ukauth.loginCallback(data);
      });
   },
   oneClickLogin: () => {
      window.location.href = UKAUTH_BASE_URL + "/app/" + ukauth.appDescription.APP_ID + "/auth";
   },
   onLogin: (callback) => {
      ukauth.loginCallback = callback;
   }
};