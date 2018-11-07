<template>
  <div :class="{checks: useImages}" :style="divStyle">
    <template v-for="i in tech.count">
      <img v-if="useImages" :src="imgFor(i-1)" class="check"/>
      <span v-else v-html="tagFor(i-1)"></span>
    </template>
  </div>
</template>

<script>
  const emptyBox = "☐"
  const checkedBox = "☑"
  const xBox = "☒"

  export default {
    name: "TechCheckmarks",
    props: ['tech', 'top', 'left', 'settings'],
    computed: {
      divStyle: function() {
        console.log("Calculating style: " + this.useImages)
        if (this.useImages) {
          let rv = {
                      top: this.top,
                      left: this.left
                    }
          console.log("Returning " + JSON.stringify(rv))
          return rv
        } else {
          return {}
        }
      },
      useImages: function() {
        return this.top && this.left
      }
    },
    methods: {
      whatIs: function(i) {
        if (i < this['tech'].drawn) {
          if (i < this['tech'].used) {
            return 'taken'
          } else {
            return 'available'
          }
        } else {
          return 'empty'
        }
      },
      imgFor: function(i) {
        let thing = this.whatIs(i)
        if (thing === 'taken') {
          return this.settings['taken_checkbox_url']
        } else if (thing === 'available') {
          return this.settings['available_checkbox_url']
        } else if (thing === 'empty') {
          return this.settings['empty_checkbox_url']
        } else {
          return "IMPOSSIBLE"
        }
      },
      tagFor: function(i) {
        let thing = this.whatIs(i)
        if (thing === 'taken') {
          return "<span style='color: red'>" + xBox + "</style>"
        } else if (thing === 'available') {
          return "<span style='color: green'>" + checkedBox + "</style>"
        } else if (thing === 'empty') {
          return "<span style='color: black'>" + emptyBox + "</style>"
        }
      }
    }

  }
</script>

<style scoped>
  .checks {
    position: absolute;
    width: 10.5%;
    text-align: center;
    font-size: 0px;
    border: solid;
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
