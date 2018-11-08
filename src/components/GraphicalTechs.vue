<template>
  <div>
    <div class="techboard-wrapper">
      <div class="techboard">
        <img :src="settings['techboard_url']" class="techboard"/>
        <tech-checkmarks v-for="tech in techs" :key="tech['key']" :tech="tech" :top="tech['top']" :left="tech['left']" :settings="settings" :socket="socket">
        </tech-checkmarks>
      </div>
    </div>

    <table style="margin: auto">
      <tr>
        <td>
          <techs-by-category2 :techs="techs" :tech-keys="categories['ship'].techs" :socket="socket" :mode="mode"></techs-by-category2>
        </td>
        <td>
          <techs-by-category2 :techs="techs" :tech-keys="categories['other'].techs" :socket="socket" :mode="mode"></techs-by-category2>
        </td>
      </tr>
    </table>
  </div>


</template>

<script>
  import TechCheckmarks from '@/components/TechCheckmarks'
  import TechsByCategory2 from '@/components/TechsByCategory2'

  export default {
    name: "GraphicalTechs",
    props: ['techs', 'socket', 'categories', 'settings', 'mode'],
    components: {
      'tech-checkmarks': TechCheckmarks,
      'techs-by-category2': TechsByCategory2
    }
  }
</script>

<style scoped>
  .techboard-wrapper {
    padding-left: 25px;
    padding-right: 25px;
  }

  .techboard {
    position: relative;
    max-width: 100%;
  }

  .checks {
    position: absolute;
    width: 10.5%;
    text-align: center;
    font-size: 0px;
  }

  .check {
    width: 15%;
    margin-left: 0%;
    margin-right: 0%;
    padding-left: 2%;
    padding-right: 2%;
    font-size: 0;
  }
</style>
