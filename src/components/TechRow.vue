<template>
  <tr>
    <td style="text-align: right"><tech-checkmarks :tech="tech"></tech-checkmarks></td>
    <td>
      <a @click="showDetails()">
        <template v-if="useDescription && tech.hasOwnProperty('description')">
          <span style="display: inline-block">
            {{ tech.description }}
          </span>
          <span style="display: inline-block">
            ({{ tech.name }})
          </span>
        </template>
        <template v-else>
          {{ tech.name }}
        </template>
      </a>
      <b-modal :active.sync="isModalActive" has-modal-card><tech-detail :tech="tech" :socket="socket"></tech-detail></b-modal>
    </td>
    <td >{{ power }}</td>
    <td style="text-align: right">{{ tech.cost }}&nbsp;/&nbsp;{{ tech.minCost }}</td>
    <template v-if="mode == 'draw'">
      <td>
        <a class="button is-success is-small" @click="draw">Draw</a>
        <!--<a class="button is-danger is-small" @click="undraw">Return</a>-->
      </td>
    </template>
    <template v-else>
      <td>
        <a class="button is-success is-small" @click="purchase">Take</a>
        <!--<a class="button is-danger is-small" @click="unpurchase">Return</a>-->
      </td>
    </template>
  </tr>
</template>

<script>
  import TechCheckmarks from "@/components/TechCheckmarks"
  import TechDetail from "@/components/TechDetail"
  import { socketMixin} from "@/mixins/WSUtils"

  export default {
    components: { TechCheckmarks, TechDetail },
    data: function() {
      return {
        isModalActive: false
      }
    },
    props: ['tech', 'socket', 'useDescription', 'mode'],
    mixins: [socketMixin],
    computed: {
      label: function() {
        let tech = this['tech']
        if (this['useDescription'] && tech.hasOwnProperty('description'))
          if (this['useDescription'] === 'only') {
            return tech.description
          } else if (this['useDescription'] === "after") {
            return `<span style='display: inline-block'>${tech.name}</span> (${tech.description})`
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
      showDetails: function() {
        this.isModalActive = true
      }
    }
  }
</script>

<style scoped>
  td {
    vertical-align: middle
  }
</style>
