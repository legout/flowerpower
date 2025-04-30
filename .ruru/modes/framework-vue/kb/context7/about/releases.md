# Vue Releases and Versioning

## Fetching Latest Vue Version with Vue and JavaScript

Fetches the latest Vue version from the GitHub API and updates a reactive reference.  It uses the Vue Composition API's `ref` and `onMounted` functions. It fetches data from the GitHub API, parses the JSON response, and assigns the version name to the `version` ref.

Source: https://github.com/vuejs/docs/blob/main/src/about/releases.md#_snippet_0

```vue
<script setup>
import { ref, onMounted } from 'vue'

const version = ref()

onMounted(async () => {
  const res = await fetch('https://api.github.com/repos/vuejs/core/releases/latest')
  version.value = (await res.json()).name
})
</script>
```

