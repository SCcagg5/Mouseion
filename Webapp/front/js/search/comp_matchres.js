let matchres = {
data: function() {
  return {
  }
},

props: {data: {default: void 0}, searchw: {default: void 0}},

filters: {
  lengthp: function(x){
    return x  + ( x == 1 ? " hit" : " hits")
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
     console.log(str);
     return str;
   }
},

methods: {
  text: function(){
    vm.$children[0].get_text(this.data.url)
  },
  escapeHtml: function (unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
  }
},

template: `
          <div>
            <div class="container result">
              <small style="top: -15px; position: relative; font-size: 60%"> {{ data.date }} </small>
              <div class="row inside" style="margin-top: -14px;">
                <div class="mr-2 btn btn-primary small-btn">{{ data.lang }}</div>
                <div style="max-width: calc(100% - 91px);">{{ decodeURI(data.title) | hex_asc | old_hex }}</div>
                <a :href=data.url class="ml-auto mr-2"><img class="img-icon " src="./imgs/pdf.svg"></img></a>
                <img  v-on:click=text() class="img-icon" style="height: 23px;" src="./imgs/external.svg"></img>
              </div>
              <div class="row inside" v-if="data.match">
                <div class="side">
                </div>
                <div class="col-12" style="padding-right: 0px;flex: 0 0 97%;max-width: 97%;padding-left: 6px;">
                  <div>
                    <div class="btn btn-secondary small-btn mr-2">{{ data.match.number | lengthp }}</div>
                  </div>
                  <div class="extract">
                    <div></div>
                    <div v-if="data.match.text">
                      <span v-for="i in (data.match.text.length > 4 ? 4 : data.match.text.length)" :inner-html.prop=" data.match.text[i - 1] | reg(searchw, escapeHtml)">
                      </span>
                    </div>
                    <div v-if="data.match.fuzzy && !data.match.perfect">
                      <span v-for="i in (data.match.fuzzy.length > 4 ? 4 : data.match.fuzzy.length)" :inner-html.prop=" data.match.fuzzy.data[i - 1] | reg(searchw, escapeHtml)">
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
         `
}
