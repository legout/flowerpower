# Vue.js Production Deployment Guide

## Tracking Runtime Errors with App-Level Error Handler in Vue.js

This code snippet demonstrates how to use the app-level error handler in Vue.js to report runtime errors to tracking services. It configures the `app.config.errorHandler` to catch errors, the instance where the error occurred, and additional information, enabling integration with services like Sentry or Bugsnag for error monitoring.

Source: https://github.com/vuejs/docs/blob/main/src/guide/best-practices/production-deployment.md#_snippet_0

```JavaScript
import { createApp } from 'vue'

const app = createApp(...)

app.config.errorHandler = (err, instance, info) => {
  // report error to tracking services
}
```

