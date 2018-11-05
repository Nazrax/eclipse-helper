<template>
  <div>
    <h1>By color</h1>
    <p>
      <button @click="showColor('red')">Red</button>
      <button @click="showColor('blue')">Blue</button>
      <button @click="showColor('yellow')">Yellow</button>
    </p>
    <p>{{ colors[currentColor].name }}</p>
    <techs-by-color2 :techs="techs" :tech-keys="colors[currentColor].techs" :socket="socket"></techs-by-color2>

    <ul>
      <li v-for="colorKey in sortByIndex(Object.keys(colors))">{{ colors[colorKey].name }}:
        <techs-by-color2 :techs="techs" :tech-keys="colors[colorKey].techs" :socket="socket"></techs-by-color2>
      </li>
    </ul>
  </div>
</template>

<script>
  import TechsByColor2 from '@/components/TechsByColor2'

  export default {
    name: "TechsByColor",
    props: ['colors', 'techs', 'socket'],
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
          console.log(`${keyA}: ${a}, ${keyB}: ${b}`)
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
