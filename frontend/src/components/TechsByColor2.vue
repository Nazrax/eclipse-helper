<template>
  <table border="1">
    <tr><td>Name</td><td>Power</td><td>Cost</td><td>Used</td><td>Drawn</td><td>Purchased</td></tr>
    <tr is="tech-row" v-for="techKey in techKeys" v-bind:tech="techs[techKey]" v-bind:socket="socket" use-description="true"></tr>
  </table>
</template>

<script>
  import TechRow from '@/components/TechRow'

  export default {
    name: "TechsByColor2",
    props: ['techs', 'techKeys', 'socket'],
    components: {
      'tech-row': TechRow
    }
  }
</script>

<style scoped>

</style>
