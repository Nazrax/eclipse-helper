<template>
  <tr>
    <td style="text-align: right"><tech-checkmarks :tech="tech"></tech-checkmarks></td>
    <td>{{ label }}</td>
    <td >{{ power }}</td>
    <td style="text-align: right">{{ tech.cost }} / {{ tech.minCost }}</td>
    <template v-if="mode == 'draw'">
      <td><a class="button is-success is-small" @click="draw">Draw</a><a class="button is-danger is-small" @click="undraw">Return</a></td>
    </template>
    <template v-else>
      <td><a class="button is-success is-small" @click="purchase">Take</a><a class="button is-danger is-small" @click="unpurchase">Return</a></td>
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
          if (this['useDescription'] === 'only') {
            return tech.description
          } else if (this['useDescription'] === "after") {
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
  td {
    vertical-align: middle
  }
</style>
