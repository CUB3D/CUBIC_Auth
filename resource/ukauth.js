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

        const socketId = uuidv4();

        // Create WebSocket connection.
        const socket = new WebSocket('wss://cbns.cub3d.pw/poll/' + socketId);

        // Connection opened
        socket.addEventListener('open', function (event) {
            console.log("Socket open");
        });

        // Listen for messages
        socket.addEventListener('message', function (event) {
            let data = JSON.parse(event.data);
            let jwt = data.dataPayload.find((x) => x.key === "JWT").value;

            document.cookie = "UK_APP_AUTH=" + jwt + "; expires=Thu, 01 Jan 2025 00:00:00 UTC; path=/;";
        });

        document.getElementById("CUBIC_LOGIN").onclick = () => {
            window.open(UKAUTH_BASE_URL + "/app/" + this.appDescription.APP_ID + "/" + socketId + "/auth",'1571170077900','width=700,height=500,toolbar=0,menubar=0,location=0,status=1,scrollbars=1,resizable=1,left=0,top=0');
        };

        // get(UKAUTH_BASE_URL + "/api/app/" + this.appDescription.APP_ID + "/user/details", (data) => {
        //     console.log(data);
        //     ukauth.loginCallback(data);
        // });
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

function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        let r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}


let UKAUTH_BASE_URL = "http://localhost:8080";
