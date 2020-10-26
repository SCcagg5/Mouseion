let cred = {
  methods: {
    api_cred: function(force = false, reload = false) {
      if (!force && localStorage.api_token && this.checktime("api_token"))
        return;
      this.ajaxRequest = true;
      data = {
         "pass" : "password"
       };
      url = method + "://" + api + "/login"
      axios.post(url, data)
           .then(
             response => {
               if (response.data.status == 200)
               {
                 localStorage.api_token = response.data.data.token;
                 localStorage.api_token_exp = this.time(response.data.data.exp);
                 if (reload == true){
                   document.location.reload(true)
                 }
               }
             });
     },
     time: function(exp = null){
       if (exp == null)
          return Math.round(new Date().getTime()/1000);
       time = Math.round(new Date(exp).getTime()/1000);
       return (time)
     },
     checktime: function(str)  {
       if (localStorage[str+"_exp"] < this.time() - 500) {
          localStorage.removeItem(str);
          localStorage.removeItem(str + "_exp");
          return false;
       }
       return true;
     },
     get_headers: function() {
       res = {}
       this.api_cred();
       res["token"] = localStorage.api_token;
       return res;
     }
   }
};
