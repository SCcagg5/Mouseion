let search = {
data: function() {
  return {
    searchword: "",
    sear: true,
    load: false,
    recu: false,
    data: void 0,
    text: void 0,
    lang: "fr"
  }
},

components: {container, warning, matchres},

props: {data: {default: void 0}},

filters:{
  tostr: function(timestamp) {
    let actual = parseInt(new Date().getTime());
    let date = parseInt(timestamp)
    let last = actual - date;
    let min = Math.floor((last/1000/60) << 0);
    return min
  },
  reg: function( str, searchw, filter){
    const reg = new RegExp(searchw, 'gi')
    reg.test(str);
    return filter(str.slice(0, reg.lastIndex - searchw.length)) +
          "<div class='regex'>" +
           filter(str.slice(reg.lastIndex - searchw.length, reg.lastIndex)) +
           "</div>" +
           filter(str.slice(reg.lastIndex, str.length)) + " ... "
  },
  hex_asc: function(hexx) {
    if (hexx[0] != '<' || hexx.replace("<FEFF", '') == hexx) {
      if (hexx[0] == '\\'){
        hexx = unescape((hexx + "").replace(/\\u([\d\w]{3})/gi, ""));
        console.log(hexx);
       }
      return hexx;
    }
    var hex = hexx.replace("<", '').replace('>', '').toString();
  	var str = '';
  	for (var n = 0; n < hex.length; n += 2) {
  		str += String.fromCharCode(parseInt(hex.substr(n, 2), 16));
  	}
  	return str;
  },
   old_hex: function(str){
     if (str[0] != 'þ' || str[1] != 'ÿ'){
       return str;
     }
     str = str.replace(/\0/g, '').substring(2);
     if (str == ""){
       return "No title";
     }
     return str;
   }
},

methods: {
  submit: function(){
    if (this.searchword == ""){
      return;
    }
    this.sear = false
    this.recu = false;
    setTimeout(this.switchload, 350);
    let data = {}
    data = cred.methods.get_headers()
    let param = '?search=' + this.searchword
    url  = 'search/' + this.lang + param
    location.href = "https" + "://" +  "mouseion.online" + "#" + url
    user.methods.retrieve(url , data, this.result);
  },

  result: function(data){
    console.log(data);
    this.recu = true
    this.load = false
    this.sear = true
    this.data = data
  },

  get_text: function(url){
    this.sear = false;
    this.recu = false;
    setTimeout(this.switchload, 350);
    let data = {}
      data['headers'] = cred.methods.get_headers()
      data['data'] = {
        'url': url
      }
      user.methods.send('text/', data, this.result_text);
  },

  result_text: function(data){
    console.log(data);
    this.recu = true
    this.load = false
    this.sear = true
    this.text = data.text
  },

  switchload: function(state = void 0){
    if (this.recu == false)
      this.load = state ? state: !this.load;
  },

  back_search: function(){
    this.recu = false
    this.load = false
    this.sear = true
    this.data = void 0;
  },

  back_result: function(){
    this.recu = true
    this.load = false
    this.sear = false
    this.text = void 0;
  },


},

mounted(){

},

template: `
          <div class="main">
            <div class="title">
              <h1>
                  Mouseîon
              </h1>
              <h5>
              PDF search engine
              </h5>
            </div>
            <div class="container_search" :class="data || text ? 'behind' : '' " v-on:keyup.enter="submit">
              <div class="lds-ripple" :class="load && !recu ? 'appear' : 'disappear' " ><div></div><div></div></div>
              <div :class="sear && !recu ? 'appear' : 'disappear'">
                <input id="input" tabindex="0" type="text" placeholder="Search..." v-model="searchword" >
                <div class="search"></div>
              </div>
            </div>
            <div v-if="recu && data && !text && !load" class="res">
              <div v-on:click=back_search() class="back"><span class="dart">←</span><div class="back-text">Back to search</div></div>
              <ul v-for="match in data.result">
                <matchres :searchw=searchword :data=match></matchres>
              </ul>
              <div v-if="data.possible.length > 0" class="probable-container">
                <h5 class="may">May Interest you ...</h5>
                <div v-for="match in data.possible" class="probable">
                  <span class="may-dart"><b>></b></span>
                  <div class="mr-2 btn btn-primary small-btn">{{ match.lang }}</div>
                  <div>{{ decodeURI(match.title) | hex_asc | old_hex  }}</div>
                </div>
              </div>
            </div>
            <div v-if="recu && data && text && !load">
              <div v-on:click=back_result() class="back-res"><span class="dart">←</span><div class="back-text">Back to search results</div></div>
              <div class="text-sup">
              <div class="mr-2 btn btn-primary text-sup">{{ text.lang }}</div>
              <div class="title-text">{{ decodeURI(text.title) | hex_asc | old_hex }}</div>
              </div>
              <br>
              <pre class="text">
                {{ text.text }}
              </pre>
            </div>
            <div :class="sear && !recu  ? 'appear' : 'disappear'">
              <img  class="fontimage" src="./imgs/fill.png">
            </div>
          </div>
         `
}
