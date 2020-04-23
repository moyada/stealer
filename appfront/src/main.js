// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

// 引入 element-ui
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
Vue.use(ElementUI)

// 引入 axios
import axios from 'axios'
Vue.prototype.$axios = axios

Vue.config.productionTip = false

function blobToString(b) {
    let u, x;
    u = URL.createObjectURL(b);
    x = new XMLHttpRequest();
    x.open('GET', u, false); // although sync, you're not fetching over internet
    x.send();
    URL.revokeObjectURL(u);
    return x.responseText;
}

Vue.mixin({
  methods: {
    blobToString: (b) => {
      return blobToString(b)
    },
    getErrData:(error) => {
    // Error 😨
      let data;
      if (error.response) {
        /*
           * The request was made and the server responded with a
           * status code that falls out of the range of 2xx
           */
        if (error.response.request.responseType === 'blob') {
          data = blobToString(error.response.data);
        } else {
          data = error.response.data
        }

        // console.log(error.response.data);
        // console.log(error.response.status);
        // console.log(error.response.headers);
        // console.log(error.response);
      } else if (error.request) {
        /*
           * The request was made but no response was received, `error.request`
           * is an instance of XMLHttpRequest in the browser and an instance
           * of http.ClientRequest in Node.js
           */
        data = error
        // console.log(error.request);
      } else {
        // Something happened in setting up the request and triggered an Error
        data = error.message
        // console.log('Error', error.message);
      }
      return data
    }
  }
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  axios,
  components: { App },
  template: '<App/>'
})
