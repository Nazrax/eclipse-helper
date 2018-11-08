<template>
  <table border="1" style="margin:auto">
    <tr><td>Avail</td><td>Name</td><td>⚡</td><td>Cost</td><td>{{mode}}</td></tr>
    <tr is="tech-row" v-for="techKey in techKeys" v-bind:tech="techs[techKey]" v-bind:socket="socket" :mode="mode"></tr>
  </table>
</template>

<script>
  import TechRow from '@/components/TechRow'

  export default {
    name: "TechsByColor2",
    props: ['techs', 'techKeys', 'socket', 'mode'],
    components: {
      'tech-row': TechRow
    }
  }
</script>

<style scoped>

</style>
