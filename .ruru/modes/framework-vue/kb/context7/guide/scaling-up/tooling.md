# Vue Tooling Guide

## Scaffold Vue Project with npm

This command uses npm to execute the create-vue scaffolding tool, which helps set up a new Vue project with a recommended project structure and configuration. It is a quick way to start a new Vue project using the latest best practices.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/tooling.md#_snippet_0

```sh
$ npm create vue@latest
```

---

## Scaffold Vue Project with Yarn Legacy

This command uses yarn dlx to execute the create-vue scaffolding tool. dlx allows for running packages without globally installing them. This is specifically for yarn versions before v4.11

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/tooling.md#_snippet_3

```sh
# For Yarn ^v4.11
$ yarn dlx create-vue@latest
```

---

## Scaffold Vue Project with bun

This command utilizes bun to execute the create-vue scaffolding tool. It creates a new Vue project, utilizing bun as the package manager, offering an alternative to npm, yarn, or pnpm.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/tooling.md#_snippet_4

```sh
$ bun create vue@latest
```

---

## Scaffold Vue Project with Yarn Modern

This command uses Yarn to execute the create-vue scaffolding tool for Yarn Modern (v2+). It initializes a new Vue project using Yarn as the package manager. Yarn Modern has different execution patterns compared to older Yarn versions, so this command is tailored for it.

Source: https://github.com/vuejs/docs/blob/main/src/guide/scaling-up/tooling.md#_snippet_2

```sh
# For Yarn Modern (v2+)
$ yarn create vue@latest
```

