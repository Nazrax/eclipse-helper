<template>
  <tr>
    <td>{{ label }}</td>
    <td>{{ power }}</td>
    <td>{{ tech.cost }} / {{ tech.minCost }}</td>
    <td><tech-checkmarks :tech="tech"></tech-checkmarks></td>
    <td>{{ tech.drawn }}/{{ tech.count }} <button @click="draw">Draw</button><button @click="undraw">Undraw</button></td>
    <td>{{ tech.used }}/{{tech.drawn}} <button @click="purchase">Purchase</button><button @click="unpurchase">Unpurchase</button></td>
  </tr>
</template>

<script>
  import TechCheckmarks from "./TechCheckmarks"
  export default {
    components: {TechCheckmarks},
    props: ['tech', 'socket', 'useDescription'],
    computed: {
      label: function() {
        let tech = this['tech']
        if (this['useDescription'] && tech.hasOwnProperty('description'))
          if (this['useDescription'] === "after") {
            return `${tech.name} (${tech.description})`
          } else {
            return `${tech.description} (${tech.name})`
          }
        else
          return tech.name
      },
      power: function() {
        return this['tech'].hasOwnProperty('power') ? `${this['tech'].power}⚡`  : ''
      },
    },
    methods: {
      draw: function() {
        console.log("Drawing")
        this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'drawn', action: "inc"}))
      },
      undraw: function() {
        console.log("Undrawing")
        this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'drawn', action: "dec"}))
      },
      purchase: function() {
        console.log("Purchasing")
        this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'used', action: "inc"}))
      },
      unpurchase: function() {
        console.log("Unpurchasing")
        this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'used', action: "dec"}))
      },
    },
  }
</script>

<style scoped>

</style>
