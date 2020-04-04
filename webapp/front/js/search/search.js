let vm = new Vue({
    el: '#search',

    data: function(){
      return {
        email: localStorage.email,
        data: ''
      }
    },

    components: {msg, leftnav, mod, search},

    methods: {

      infos: function(res) {
        let data = {}
        data['headers'] = cred.methods.get_headers()
        data['data'] = {}
        user.methods.send('points/infos', data, this.store);
      },

      store: function(data) {
        if (data != '') {
          localStorage.points = JSON.stringify(data['points']);
          this.data = data['points'];
        }
      },
   },
   mounted(){
     cred.methods.api_cred(true)
   }
})
