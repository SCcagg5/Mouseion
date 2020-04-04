let matchres = {
data: function() {
  return {
  }
},

props: {data: {default: void 0}, searchw: {default: void 0}},

filters: {
  lengthp: function(x){
    return (x == 20 ? "+20" : x)  + ( x == 1 ? " hit" : " hits")
  },
  lengthf: function(x){
    return (x == 20 ? "+20" : x) + ( x == 1 ? " partial hit" : " partials hits")
  },
  reg: function( str, searchw, filter){
    const reg = new RegExp(searchw, 'gi')
    reg.test(str);
    return filter(str.slice(0, reg.lastIndex - searchw.length)) +
          "<div class='regex'>" +
           filter(str.slice(reg.lastIndex - searchw.length, reg.lastIndex)) +
           "</div>" +
           filter(str.slice(reg.lastIndex, str.length)) + " ... "
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
              <div class="row inside">
                <div class="mr-2 btn btn-primary small-btn">{{ data.lang }}</div>
                <div>{{ data.title }}</div>
                <a :href=data.url class="ml-auto mr-2"><img class="img-icon " src="./imgs/pdf.svg"></img></a>
                <img  v-on:click=text() class="img-icon" style="height: 23px;" src="./imgs/external.svg"></img>
              </div>
              <div class="row inside" v-if="data.match">
                <div class="side">
                </div>
                <div class="col-12" style="padding-right: 0px;flex: 0 0 97%;max-width: 97%;padding-left: 6px;">
                  <div>
                    <div v-if="data.match.perfect" class="btn btn-secondary small-btn mr-2">{{ data.match.perfect.length | lengthp }}</div>
                    <div v-if="data.match.fuzzy" class="btn btn-secondary small-btn ">{{ data.match.fuzzy.length | lengthf }}</div>
                  </div>
                  <div class="extract">
                    <div></div>
                    <div v-if="data.match.perfect">
                      <span v-for="i in (data.match.perfect.length > 4 ? 4 : data.match.perfect.length)" :inner-html.prop=" data.match.perfect.data[i - 1] | reg(searchw, escapeHtml)">
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
