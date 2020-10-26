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
   },
   mounted(){
     cred.methods.api_cred(true)
   }
})
