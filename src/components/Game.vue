<template>
  <div>
    <nav class="navbar is-dark is-fixed-top" role="navigation" aria-label="dropdown navigation">
      <div class="navbar-brand">
        <a @click="handleRoundClicked()" class="navbar-item">Round {{round}}/9</a>
        <div class="navbar-item">
          <div class="buttons">
            <a class="button" :class="[mode === 'take' ? 'is-primary' : 'is-light']" @click="handleTakeButton()">Take</a>
            <a class="button" :class="[mode === 'draw' ? 'is-primary' : 'is-light']" @click="handleDrawButton()">Draw</a>
          </div>
        </div>
        <a role="button" class="navbar-burger burger" :class="burgerActive" aria-label="menu" aria-expanded="false" data-target="navbarBasicExample" @click="handleBurger()">
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </a>
      </div>

      <div class="navbar-menu" :class="burgerActive">
        <div class="navbar-start">
          <a class="navbar-item" @click="setComponent('techs-by-category')">
            By Category
          </a>
          <a class="navbar-item" @click="setComponent('techs-by-color')">
            By Color
          </a>
          <a class="navbar-item" @click="setComponent('all-techs')">
            By Name
          </a>
          <a class="navbar-item" @click="setComponent('graphical-techs')">
            Grid
          </a>
        </div>
      </div>
      <div class="navbar-end">
      </div>
    </nav>
    <p>&nbsp;
    </p>

    <component :is="currentComponent" :categories="categories" :colors="colors" :techs="techs" :socket="socket" :settings="settings" :mode="mode"></component>

    <div class="fixed-footer" v-if="showRoundPrompt">
      <div class="centered">
        Round started {{ roundMinutes }} minutes ago.
        <a class="button is-warning is-small"@click="startNewRound()">Start new round</a>
      </div>
    </div>
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
        settings: {},
        mode: 'take',
        showBurgerMenu: false,
        round: 0,
        roundStartedAt: 0,
        epoch: this.calculateEpoch(),
        connecting: false
      }
    },
    computed: {
      burgerActive: function() {
        return {'is-active': this.showBurgerMenu}
      },
      roundTime: function() {
        return this.epoch - this.roundStartedAt
      },
      prettyRoundTime: function() {
        let seconds = this.roundTime
        let hours = Math.floor(seconds/60/60)
        seconds -= hours*60*60
        let minutes = Math.floor(seconds/60)
        seconds -= minutes*60
        let m = minutes < 10 ? `0${minutes}` : minutes
        let s = seconds < 10 ? `0${seconds}` : seconds
        return `${hours}:${m}:${s}`
      },
      roundMinutes: function() {
        return Math.floor(this.roundTime / 60)
      },
      showRoundPrompt: function() {
        return this.round < 9 && this.mode === 'draw' && this.epoch - this.roundStartedAt > 10
      }
    },
    created: function() {
      axios.get(`/techs/${this.id}.json`)
        .then(response => {
          this.techs = response.data.techs
          this.categories = response.data.categories
          this.colors = response.data.colors
          this.settings = response.data.settings
          this.round = response.data.round
          this.roundStartedAt = response.data['round_time']
        })
        .catch(e => {
          console.log("Axios error: " + e)
        })
    },
    mounted: function() {
      this.connect()
      document.title = `Eclipse: ${this.id}`
      let ths = this
      setInterval(function() {
        ths.epoch = ths.calculateEpoch()
      }, 1000)
    },
    beforeDestroy: function() {
      console.log("beforeDestroy() hook; closing socket")
      try {
        this.socket.onclose = null
        this.socket.onerror = null
        this.socket.close()
      } catch (err) {}
    },
    methods: {
      startNewRound: function() {
        this.sendRound(this.round + 1)
      },
      calculateEpoch: function() {
        return Math.floor((new Date).getTime()/1000)
      },
      handleTakeButton: function() {
        this.mode = 'take'
      },
      handleDrawButton: function() {
        this.mode = 'draw'
      },
      handleBurger: function() {
        this.showBurgerMenu = !this.showBurgerMenu
      },
      handleRoundClicked: function() {
        this.$dialog.prompt({
          message: "Current round?",
          inputAttrs: {
            type: 'number',
            placeholder: 'Round #',
            value: this.round,
            max: 9,
            min: 1
          },
          onConfirm: (value) => this.sendRound(value)
        })
      },
      sendRound: function(value) {
        this['socket'].send(JSON.stringify({type: 'round', round: value}))
      },
      handleMessage: function(event) {
        // console.log(`Got '${event.data}' from socket`)
        let parsed = JSON.parse(event.data)
        if (parsed['type'] === 'tech') {
          // console.log(` - Tech: Setting ${parsed['key']}:${parsed['field']} to ${parsed['value']}`)
          let tech = this.techs[parsed['key']]
          this.$set(tech, parsed['field'], parsed['value'])
        } else if (parsed['type'] === 'round') {
          this.round = parsed['round']
          this.roundStartedAt = parsed['time']
          console.log("Round is now " + this.round)
        } else {
          console.log(` - Unknown message type ${parsed}`)
          return
        }
        if(parsed.hasOwnProperty('toast') && parsed['toast'] !== '') {
          this.$toast.open({duration: 3000, message: parsed['toast'], queue: false})
          let foo="1     "
        }
       },
      setComponent: function(component) {
        this.currentComponent = component
      },
      connect: function() {
        console.log(this)

        if (this.connecting) {
          console.log("Connection already in progress")
          return
        }
        let proto = location.protocol === 'https:' ? 'wss' : 'ws'
        let url = `${proto}://${location.host}/websocket/${this.id}`
        console.log(`Connecting to websocket URL ${url}`)
        let socket = new WebSocket(url)
        socket.onopen = this.handleSocketConnected
        socket.onmessage = this.handleMessage
        socket.onclose = this.handleSocketClosed
        socket.onerror = this.handleSocketError
        this.reconnectScheduled = false
        this.connecting = true
      },
      reconnect: function() {
        if (this.reconnectScheduled) {
          console.log("Reconnect already scheduled; not scheduling a new one")
        } else {
          this.reconnectScheduled = true
          console.log("Reconnect(): Websocket connection failed/died; trying again in 5 seconds")
          setTimeout(this.connect, 5000)
        }
      },
      handleSocketConnected: function(event) {
        this.connecting = false
        console.log("Connection established")
        console.log(event)

        if (this.socket != null) {
          console.log(" Existing Socket ready state: " + this.socket.readyState)
          if (this.socket.readyState === 1) {
            console.log("Closing stale connection")
            this.socket.close()
          }
        } else {
          console.log(" - Existing socket is null")
        }
        this.socket = event.currentTarget
        this.doPing()
      },
      handleSocketClosed: function(event) {
        this.connecting = false

        console.log("handleSocketClosed()")
        if (this.socket.readyState === 1) {
          console.log(" - this.socket is still connected; ignoring event")
        } else {
          console.log(" - Triggering reconnect")
          this.reconnect()
        }
      },
      handleSocketError: function(event) {
        this.connecting = false

        console.log("handleSocketError():")
        console.log(event)
        if (this.socket.readyState !== 1) {
          console.log(" - Websocket connection had an error and disconnected; calling reconnect")
          this.reconnect()
        }
      },
      doPing: function() {
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
  .fixed-footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: cyan;
    color: black;
    text-align: center;
    vertical-align: middle;
    font-size: 125%;
    height: 50px;
  }
  .centered {
    margin: 0;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 100%;
  }
</style>
