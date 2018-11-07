<template>
  <div :class="{checks: useImages}" :style="divStyle">
    <template v-for="i in tech.count">
      <img v-if="useImages" :src="imgFor(i-1)" @click="handleClick(i-1)" class="check"/>
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
    props: ['tech', 'top', 'left', 'settings', 'socket'],
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
      handleClick: function(i) {
        let drawn = this['tech'].drawn
        let used = this['tech'].used
        if (i === drawn) {
          this.draw()
        } else if (i === used && i < drawn) {
          this.purchase()
        } else if (i === used-1 && i === drawn-1) {
          this.unpurchase()
          this.undraw()
        } else if (i === drawn-1) {
          this.undraw()
        }
      },
      draw: function() {  // TODO Extract these into some kind of utility class
        this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'drawn', action: "inc"}))
      },
      undraw: function() {
        this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'drawn', action: "dec"}))
      },
      purchase: function() {
        this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'used', action: "inc"}))
      },
      unpurchase: function() {
        this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'used', action: "dec"}))
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
