<template>
  <div>
    <p>This is game {{ id }}</p>

    <button @click="setComponent('techs-by-category')">Categories</button>
    <button @click="setComponent('techs-by-color')">Colors</button>
    <button @click="setComponent('all-techs')">All</button>
    <button @click="setComponent('graphical-techs')">Graphical</button>

    <component :is="currentComponent" :categories="categories" :colors="colors" :techs="techs" :socket="socket" :settings="settings"></component>
  </div>
</template>

<script>
  import axios from 'axios'
  import TechsByColor from '@/components/TechsByColor'
  import TechsByCategory from '@/components/TechsByCategory'
  import AllTechs from '@/components/AllTechs'
  import GraphicalTechs from '@/components/GraphicalTechs'

  export default {
    name: "Game",
    props: ['id'],
    data: function() {
      return {
        techs: {},
        categories: {},
        colors: {},
        socket: null,
        currentComponent: 'techs-by-category',
        reconnectScheduled: false,
        settings: {}
      }
    },
    created: function() {
      axios.get(`/techs/${this.id}.json`)
        .then(response => {
          this.techs = response.data.techs
          this.categories = response.data.categories
          this.colors = response.data.colors
        })
        .catch(e => {
          console.log("Axios error: " + e)
        })
      axios.get('/settings.json')
        .then(response => {
          this.settings = response.data
        })
        .catch(e => {
          console.log("Axios error: " + e)
        })
    },
    mounted: function() {
      this.connect()
      document.title = `Eclipse: ${this.id}`
    },
    methods: {
      'handleMessage': function(event) {
        console.log(`Got '${event.data}' from socket`)
        let parsed = JSON.parse(event.data)
        console.log(`Setting ${parsed['key']}:${parsed['field']} to ${parsed['value']}`)
        let tech = this.techs[parsed['key']]
        this.$set(tech, parsed['field'], parsed['value'])
      },
      'setComponent': function(component) {
        this.currentComponent = component
      },
      'connect': function() {
        let proto = location.protocol === 'https:' ? 'wss' : 'ws'
        let url = `${proto}://${location.host}/websocket/${this.id}`
        console.log(`Connecting to websocket URL ${url}`)

        this.socket = new WebSocket(url)
        this.socket.onopen = this.handleSocketConnected
        this.socket.onmessage = this.handleMessage
        this.socket.onclose = this.handleSocketClosed
        this.socket.onerror = this.handleSocketError
        this.reconnectScheduled = false
      },
      'reconnect': function() {
        if (this.reconnectScheduled) {  // Race condition!
          console.log("Reconnect already scheduled; not scheduling a new one")
        } else {
          this.reconnectScheduled = true
          console.log("Reconnect(): Websocket connection failed/died; trying again in 5 seconds")
          setTimeout(this.connect, 5000)
        }
      },
      'handleSocketConnected': function(event) {
        console.log("Connection established")
        this.doPing()
      },
      'handleSocketClosed': function(event) {
        console.log("handleSocketClosed(): Calling reconnect")
        this.reconnect()
      },
      'handleSocketError': function(event) {
        console.log("handleSocketError(): " + event)
        if (this.socket.readyState !== 1) {
          console.log(" - Websocket connection had an error and disconnected; calling reconnect")
          this.reconnect()
        }
      },
      'doPing': function() {
        if (this.socket.readyState === 1) {
          this.socket.send(JSON.stringify({type: "ping"}))
          setTimeout(this.doPing, 20000)
        } else {
          console.log("Websocket died; stopping ping")
        }
      }

    },
    components: {
      'techs-by-color': TechsByColor,
      'techs-by-category': TechsByCategory,
      'all-techs': AllTechs,
      'graphical-techs': GraphicalTechs
    }
  }
</script>

<style scoped>

</style>
