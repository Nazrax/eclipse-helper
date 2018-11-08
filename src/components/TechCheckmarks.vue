<template>
  <div :class="{checks: useImages}" :style="divStyle">
    <template v-for="i in tech.count">
      <img v-if="useImages" :src="imgFor(i-1)" @click="handleClick(i-1)" class="check"/>
      <span v-else v-html="tagFor(i-1)" class="text-checks centered"></span>
    </template>
  </div>
</template>

<script>
  import { socketMixin} from "@/mixins/WSUtils"

  const emptyBox = "☐"
  const checkedBox = "☑"
  const xBox = "☒"

  export default {
    name: "TechCheckmarks",
    props: ['tech', 'top', 'left', 'settings', 'socket', 'mode'],
    mixins: [socketMixin],
    computed: {
      divStyle: function() {
        if (this.useImages) {
          let rv = {
                      top: this.top,
                      left: this.left
                    }
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
      handleClick: function(i) {
        let drawn = this['tech'].drawn
        let used = this['tech'].used
        console.log(`I: ${i} D: ${drawn} U: ${used} M: ${this.mode}`)
        if (this.mode === 'draw') {
          if (i === drawn) {
            this.draw()
          } else if (i === drawn - 1 && i >= used) {
            this.undraw()
          }
        } else if (this.mode === 'take') {
          if (i === used && i < drawn) {
            this.purchase()
          } else if (i === used - 1) {
            this.unpurchase()
          }
        }
      },
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
          return "/images/techboard/taken_checkbox.png"
        } else if (thing === 'available') {
          return "/images/techboard/available_checkbox.png"
        } else if (thing === 'empty') {
          return "/images/techboard/empty_checkbox.png"
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
  }

  .check {
    width: 18%;
    margin-left: 0%;
    margin-right: 0%;
    padding-left: 2%;
    padding-right: 2%;
    font-size: 0;
  }

  .text-checks {
    font-size: 125%;
    margin-top: 0;
    margin-bottom: 0;
    padding-top: 0;
    padding-bottom: 0;
  }
</style>
