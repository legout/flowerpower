# Vue.js Sponsor Information

## Vue Component Setup and Lifecycle Hook

This code snippet demonstrates a Vue component setup using the `<script setup>` syntax. It imports necessary modules from Vue and a custom component. The `onMounted` lifecycle hook is used to call the `load` function when the component is mounted.

Source: https://github.com/vuejs/docs/blob/main/src/sponsor/index.md#_snippet_0

```vue
<script setup>
import SponsorsGroup from '@theme/components/SponsorsGroup.vue'
import { load, data } from '@theme/components/sponsors'
import { onMounted } from 'vue'

onMounted(load)
</script>
```

