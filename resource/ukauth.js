let ukauth = {
   oneClickLogin: function(appDescription) {
      // window.location.href = "https://auth.cub3d.pw/auth/app/" + appDescription.APP_ID;
      window.location.href = "http://localhost:8080/app/" + appDescription.APP_ID + "/auth";

   }
};