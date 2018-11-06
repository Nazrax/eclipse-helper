import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import Game from '@/components/Game'
import NotFound from '@/components/NotFound'

Vue.use(Router)

export default new Router({
  routes: [
    { path: '/', component: Home },
    { path: '/g/:id', component: Game, props: true },
    { path: '*', component: NotFound},
  ],
  mode: 'history'
})
