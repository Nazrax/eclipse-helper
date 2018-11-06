<template>
  <tr>
    <td>{{ label }}</td>
    <td>{{ power }}</td>
    <td>{{ tech.cost }} / {{ tech.minCost }}</td>
    <td v-html="used"></td>
    <td>{{ tech.drawn }}/{{ tech.count }} <button @click="draw">Draw</button><button @click="undraw">Undraw</button></td>
    <td>{{ tech.used }}/{{tech.drawn}} <button @click="purchase">Purchase</button><button @click="unpurchase">Unpurchase</button></td>
  </tr>
</template>

<script>
  const emptyBox = "☐"
  const checkedBox = "☑"
  const xBox = "☒"
  // const hex = "⬡"
  // const chevron = "^"

  export default {
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
      used: function() {
        let rv = ""
        for(let i=0; i<this['tech'].count; i++) {
          if (i < this['tech'].drawn) {
            if (i < this['tech'].used) {
              rv += "<color='red'>" + xBox + "</color>"
            } else {
              rv += "<color='green'>" + checkedBox + "</color>"
            }
          } else {
            rv += "<color='black'>" + emptyBox + "</color>"
          }
        }
        return rv
      }
    },
    methods: {
      draw: function() {
        console.log("Drawing")
        this['socket'].send(JSON.stringify({key: this['tech'].key, field: 'drawn', action: "inc"}))
      },
      undraw: function() {
        console.log("Undrawing")
        this['socket'].send(JSON.stringify({key: this['tech'].key, field: 'drawn', action: "dec"}))
      },
      purchase: function() {
        console.log("Purchasing")
        this['socket'].send(JSON.stringify({key: this['tech'].key, field: 'used', action: "inc"}))
      },
      unpurchase: function() {
        console.log("Unpurchasing")
        this['socket'].send(JSON.stringify({key: this['tech'].key, field: 'used', action: "dec"}))
      },
    },
  }
</script>

<style scoped>

</style>
