let ukauth = {
   oneClickLogin: function(appDescription) {
      let base_url = "https://auth.cub3d.pw";

      window.location.href = base_url + "/app/" + appDescription.APP_ID + "/auth";
   }
};