let user = {
  methods: {
    retrieve: function(route, headers, callback) {
      url = method + "://" + api + '/' + route + '/';
      this.callapi(url, {headers: headers}, callback, 'GET')
    },

    send: function(route, data, callback){
      url = method + "://" + api + '/' + route + '/';
      this.callapi(url, data, callback, 'POST')
    },

    callapi: function(url, data, callback, req_method = 'GET'){
      this.ajaxRequest = true;
      if (req_method == 'GET') {
        axios.get(url, { headers: data.headers})
          .then(response => this.relay(response.data, callback, false))
          .catch(error => this.error(error));
      } else {
        axios.post(url, data.data, { headers: data.headers})
          .then(response => this.relay(response.data, callback, false))
          .catch(error => this.error(error));
      }
    },

    relay: function(data, callback, redirect = true , message = false) {
      if (data.status != 200){
         if (data.error == 'Invalid token'){
           cred.methods.api_cred(true);
         }
         let type = "error";
         console.log(data.error, type);
         return;
       }
       return callback(data.data);
    },

    error: function(error) {
      console.log(String(error), "error")
    },
  }
}
