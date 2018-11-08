<template>
  <div class="columns is-centered">
    <div class="column">
      <div style="font-size: 150%; text-align: center ">All Technologies</div>
      <table border="1" style="margin:auto">
        <tr><td>Avail</td><td>Name</td><td>⚡</td><td>Cost</td><td></td></tr>
        <tr is="tech-row" v-for="techKey in sortByName(Object.keys(techs))" :tech="techs[techKey]" :socket="socket"></tr>
      </table>
    </div>
  </div>
</template>

<script>
  import TechRow from '@/components/TechRow'

  export default {
    name: "AllTechs",
    props: ['techs', 'socket'],
    components: {
      'tech-row': TechRow
    },
    methods: {
      sortByName: function(techs) {
        let sortFunc = function (keyA, keyB) {
          return keyA > keyB ? 1 : keyB > keyA ? -1 : 0
        }
        return techs.sort(sortFunc)
      }
    }
  }
</script>

<style scoped>

</style>
