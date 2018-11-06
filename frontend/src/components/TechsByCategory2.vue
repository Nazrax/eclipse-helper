<template>
  <table border="1">
    <tr><td>Name</td><td>Power</td><td>Cost</td><td>Used</td><td>Drawn</td><td>Purchased</td></tr>
    <tr is="tech-row" v-for="techKey in sortedTechKeys" v-bind:tech="techs[techKey]" v-bind:socket="socket" use-description="true"></tr>
  </table>
</template>

<script>
  import TechRow from '@/components/TechRow'

  export default {
    name: "techs-by-category2",
    props: ['techs', 'techKeys', 'socket'],
    components: {
      'tech-row': TechRow
    },
    computed: {
      sortedTechKeys: function() {
        return this.sortByLabel(this.techKeys)
      }
    },
    methods: {
      makeLabel: function(tech) {
        if (tech.hasOwnProperty('description'))
          return `${tech.description} (${tech.name})`
        else
          return tech.name
      },
      sortByLabel: function(keys) {
        let ths = this
        let sortFunc = function(keyA, keyB) {
          let a = ths.makeLabel(ths.techs[keyA])
          let b = ths.makeLabel(ths.techs[keyB])
          return a > b ? 1 : b > a ? -1 : 0
        }
        return keys.sort(sortFunc)
      }
    }
  }
</script>

<style scoped>

</style>
