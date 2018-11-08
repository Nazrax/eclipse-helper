<template>
  <div class="modal-card" style="width: auto">
    <header class="modal-card-head" style="font-weight: bold">
      {{ tech['name']}}
    </header>
    <section class="modal-card-body">
      <img :src="`/images/tiles/${tech['key']}.jpg`"/>
      <img v-if="tech['category'] === 'ship'" :src="`/images/upgrades/${tech['key']}.jpg`"/>
      <table>
        <tr v-if="tech['description']"><td colspan="2" class="tdr">Description:</td><td colspan="2">{{ tech['description'] }}</td></tr>
        <tr>
          <td class="tdr">Total Quantity:</td>
          <td>{{ tech['count'] }}</td>
        </tr>
        <tr>
          <td class="tdr">Drawn:</td>
          <td>{{ tech['drawn'] }}</td>
          <td class="tdc"><a class="button is-success is-small" @click="draw">Draw</a></td>
          <td class="tdc"><a class="button is-danger is-small" @click="undraw">Return</a></td>
        </tr>
        <tr>
          <td class="tdr">Taken:</td>
          <td>{{ tech['used'] }}</td>
          <td class="tdc"><a class="button is-success is-small" @click="purchase">Take</a></td>
          <td class="tdc"><a class="button is-danger is-small" @click="unpurchase">Return</a></td>
        </tr>
        <tr><td colspan="4" class="tdc"><tech-checkmarks :tech="tech"></tech-checkmarks></td></tr>
      </table>
    </section>
    <footer class="modal-card-foot">
      <a class="button" @click="$parent.close()">Close</a>
    </footer>
  </div>
</template>

<script>
  import { socketMixin} from "@/mixins/WSUtils"
  import TechCheckmarks from "./TechCheckmarks"

  export default {
    name: "TechDetail",
    components: {TechCheckmarks},
    props: ['tech', 'socket'],
    mixins: [socketMixin],
  }
</script>

<style scoped>
  td {
    vertical-align: middle;
  }

  .tdr {
    text-align: right;
  }

  .tdc {
    text-align: center;
  }

</style>
