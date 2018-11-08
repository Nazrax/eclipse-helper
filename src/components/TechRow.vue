<template>
  <tr>
    <td align="right"><tech-checkmarks :tech="tech"></tech-checkmarks></td>
    <td align="left">{{ label }}</td>
    <td>{{ power }}</td>
    <td>{{ tech.cost }} / {{ tech.minCost }}</td>
    <template v-if="mode == 'draw'">
      <td><button @click="draw">Draw</button><button @click="undraw">Return</button></td>
    </template>
    <template v-else>
      <td><button @click="purchase">Take</button><button @click="unpurchase">Return</button></td>
    </template>
  </tr>
</template>

<script>
  import TechCheckmarks from "./TechCheckmarks"
  import { socketMixin} from "@/mixins/WSUtils"

  export default {
    components: {TechCheckmarks},
    props: ['tech', 'socket', 'useDescription', 'mode'],
    mixins: [socketMixin],
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
    }
  }
</script>

<style scoped>

</style>
