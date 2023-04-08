import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import Video from '@/components/Video'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'video',
      component: Video

    },
    {
      path: '/test',
      name: 'HelloWorld',
      component: HelloWorld

    }
  ]
})
