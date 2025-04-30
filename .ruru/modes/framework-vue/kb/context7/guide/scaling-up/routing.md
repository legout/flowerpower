# Vue.js Routing Guide

## Simple Routing with Options API in Vue.js

This snippet demonstrates a simple client-side routing implementation in Vue.js using the Options API. It defines a `routes` object mapping URL hashes to Vue components, uses a data property to track the current path, and dynamically renders the appropriate component based on the `hashchange` event in the mounted lifecycle hook.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/routing.md#_snippet_1

```vue
<script>
import Home from './Home.vue'
import About from './About.vue'
import NotFound from './NotFound.vue'

const routes = {
  '/': Home,
  '/about': About
}

export default {
  data() {
    return {
      currentPath: window.location.hash
    }
  },
  computed: {
    currentView() {
      return routes[this.currentPath.slice(1) || '/'] || NotFound
    }
  },
  mounted() {
    window.addEventListener('hashchange', () => {
		  this.currentPath = window.location.hash
		})
  }
}
</script>

<template>
  <a href="#/">Home</a> |
  <a href="#/about">About</a> |
  <a href="#/non-existent-path">Broken Link</a>
  <component :is="currentView" />
</template>
```

---

## Simple Routing with Composition API in Vue.js

This snippet demonstrates a basic client-side routing implementation in Vue.js using the Composition API. It defines a `routes` object mapping URL hashes to Vue components, uses a `ref` to track the current path, and dynamically renders the appropriate component based on the `hashchange` event.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/routing.md#_snippet_0

```vue
<script setup>
import { ref, computed } from 'vue'
import Home from './Home.vue'
import About from './About.vue'
import NotFound from './NotFound.vue'

const routes = {
  '/': Home,
  '/about': About
}

const currentPath = ref(window.location.hash)

window.addEventListener('hashchange', () => {
  currentPath.value = window.location.hash
})

const currentView = computed(() => {
  return routes[currentPath.value.slice(1) || '/'] || NotFound
})
</script>

<template>
  <a href="#/">Home</a> |
  <a href="#/about">About</a> |
  <a href="#/non-existent-path">Broken Link</a>
  <component :is="currentView" />
</template>
```

