<template>
  <div class="columns is-centered">
    <div class="column is-narrow" v-for="colorKey in sortByIndex(Object.keys(colors))">
      <div style="font-size: 150%; text-align: center ">{{ colors[colorKey].name }}</div>
      <techs-by-color2 v-if="colors[currentColor]" :techs="techs" :tech-keys="colors[colorKey].techs" :socket="socket" :mode="mode"></techs-by-color2>
    </div>
  </div>
</template>

<script>
  import TechsByColor2 from '@/components/TechsByColor2'

  export default {
    name: "TechsByColor",
    props: ['colors', 'techs', 'socket', 'mode'],
    data: function() {
      return {
        'currentColor': 'red'
      }
    },
    components: {
      'techs-by-color2': TechsByColor2
    },
    methods: {
      sortByIndex: function(keys) {
        const ths = this
        const sortFunc = function(keyA, keyB) {
          const a = ths.colors[keyA]['index']
          const b = ths.colors[keyB]['index']
          return a > b ? 1 : b > a ? -1 : 0
        }
        return keys.sort(sortFunc)
      },
      showColor: function(color) {
        this.currentColor = color
      }
    }
  }
</script>

<style scoped>

</style>
