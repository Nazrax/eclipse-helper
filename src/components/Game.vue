<template>
  <div>
    <p>This is game {{ id }}</p>

    <button @click="setComponent('techs-by-category')">Categories</button>
    <button @click="setComponent('techs-by-color')">Colors</button>
    <button @click="setComponent('all-techs')">All</button>


    <component :is="currentComponent" :categories="categories" :colors="colors" :techs="techs" :socket="socket"></component>
  </div>
</template>

<script>
  import axios from 'axios'
  import TechsByColor from '@/components/TechsByColor'
  import TechsByCategory from '@/components/TechsByCategory'
  import AllTechs from '@/components/AllTechs'

  export default {
    name: "Game",
    props: ['id'],
    data: function() {
      return {
        techs: {},
        categories: {},
        colors: {},
        socket: null,
        currentComponent: 'techs-by-color'
      }
    },
    created() {
      axios.get(`/techs/${this.id}.json`)
        .then(response => {
          this.techs = response.data.techs
          this.categories = response.data.categories
          this.colors = response.data.colors
        })
        .catch(e => {
          console.log("Axios error: " + e)
        })
    },
    mounted: function() {
      let proto = location.protocol === 'https:' ? 'wss' : 'ws'
      let url = `${proto}://${location.host}/websocket/${this.id}`
      console.log(`Connecting to websocket URL ${url}`)
      this.socket = new WebSocket(url)
      this.socket.onmessage = this.handleMessage
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
      }

    },
    components: {
      'techs-by-color': TechsByColor,
      'techs-by-category': TechsByCategory,
      'all-techs': AllTechs
    }
  }
</script>

<style scoped>

</style>
