<template>
  <div class="hero is-fullheight is-info is-bold">
    <div class="hero-body">
      <div class="container">
        <h1 class="title has-text-centered">Create/Open Entry</h1>
        <div class="box">
          <form id="game-form" @submit.prevent="processForm">
            <b-field label="Game ID">
              <b-input v-model="gameId"></b-input>
            </b-field>
            <div class="field has-text-right">
              <button type="submit" class="button">OK</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "Home",
    data: function() {
      return {
        gameId: ''
      }
    },
    methods: {
      processForm: function() {
        this.$router.push('/g/' + this.gameId)
      }
    }
  }
</script>

<style scoped>

</style>

