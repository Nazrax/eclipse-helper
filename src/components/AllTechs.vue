<template>
  <div>
    <h1>All techs!</h1>
    <table border="1">
      <tr><td>Name</td><td>Power</td><td>Cost</td><td>Taken</td><td>Drawn</td><td>Purchased</td></tr>
      <tr is="tech-row" v-for="techKey in sortByName(Object.keys(techs))" :tech="techs[techKey]" :socket="socket"></tr>
    </table>

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
