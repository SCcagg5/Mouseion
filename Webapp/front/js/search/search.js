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

function hex_to_ascii(str1)
 {
	var hex  = str1.toString();
	var str = '';
	for (var n = 0; n < hex.length; n += 2) {
		str += String.fromCharCode(parseInt(hex.substr(n, 2), 16));
	}
	return str;
 }
console.log(hex_to_ascii('004D00690073006500200065006E0020007000610067006500200031'));
