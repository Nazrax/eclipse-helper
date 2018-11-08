<template>
  <div class="columns is-centered">
    <div class="column is-narrow" v-for="categoryKey in Object.keys(categories)">
      <div style="font-size: 150%; text-align: center ">{{ categories[categoryKey].name }}</div>
      <techs-by-category2 :techs="techs" :tech-keys="categories[categoryKey].techs" :socket="socket" :mode="mode"></techs-by-category2>
    </div>
  </div>
</template>

<script>
  import TechsByCategory2 from '@/components/TechsByCategory2'

  export default {
    name: "TechsByCategory",
    data: function() {
      return {
        currentCategory: 'other'
      }
    },
    props: ['categories', 'techs', 'socket', 'mode'],
    components: {
      'techs-by-category2': TechsByCategory2
    },
    methods: {
      showCategory: function (category) {
        this.currentCategory = category
      }
    }
  }
</script>

<style scoped>

</style>
