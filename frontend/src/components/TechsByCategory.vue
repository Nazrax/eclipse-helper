<template>
  <div>
    <h1>By category</h1>
    <ul>
      <li v-for="categoryKey in Object.keys(categories)">{{ categories[categoryKey].name }}:
        <techs-by-category2 :techs="techs" :tech-keys="categories[categoryKey].techs" :socket="socket"></techs-by-category2>
      </li>
    </ul>
  </div>
</template>

<script>
  import TechsByCategory2 from '@/components/TechsByCategory2'
  export default {
    name: "TechsByCategory",
    props: ['categories', 'techs', 'socket'],
    components: {
      'techs-by-category2': TechsByCategory2
    }
  }
</script>

<style scoped>

</style>
