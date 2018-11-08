<template>
  <div class="modal-card" style="width: auto">
    <header class="modal-card-head" style="font-weight: bold">
      {{ tech['name']}}
    </header>
    <section class="modal-card-body">
      <img :src="`/images/tiles/${tech['key']}.jpg`"/>
      <img v-if="tech['category'] === 'ship'" :src="`/images/upgrades/${tech['key']}.jpg`"/>
      <p v-if="tech['description']">{{ tech['description'] }}</p>
      Quantity: {{ tech['count'] }}<br/>
      Drawn: {{ tech['drawn'] }}<br/>
      Taken: {{ tech['used'] }}<br/>
    </section>
    <footer class="modal-card-foot">
      <a class="button" @click="$parent.close()">Close</a>
    </footer>
  </div>
</template>

<script>
  export default {
    name: "TechDetail",
    props: ['tech']
  }
</script>

<style scoped>

</style>
