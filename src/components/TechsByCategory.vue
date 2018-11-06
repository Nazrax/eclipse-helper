<template>
  <div>
    <h1>By category</h1>
    <p>
      <button @click="showCategory('ship')">Ship</button>
      <button @click="showCategory('other')">Civilization</button>
    </p>
    <p>{{ categories[currentCategory] && categories[currentCategory].name }}</p>
    <techs-by-category2 v-if="categories[currentCategory]" :techs="techs" :tech-keys="categories[currentCategory].techs" :socket="socket"></techs-by-category2>

    <!--<ul>-->
      <!--<li v-for="categoryKey in Object.keys(categories)">{{ categories[categoryKey].name }}:-->
        <!--<techs-by-category2 :techs="techs" :tech-keys="categories[categoryKey].techs" :socket="socket"></techs-by-category2>-->
      <!--</li>-->
    <!--</ul>-->
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
    props: ['categories', 'techs', 'socket'],
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
