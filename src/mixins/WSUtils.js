export const socketMixin = {
  methods: {
    draw: function () {
      this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'drawn', action: "inc"}))
    },
    undraw: function () {
      this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'drawn', action: "dec"}))
    },
    purchase: function () {
      this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'used', action: "inc"}))
    },
    unpurchase: function () {
      this['socket'].send(JSON.stringify({type: 'tech', key: this['tech'].key, field: 'used', action: "dec"}))
    },
  }
}
