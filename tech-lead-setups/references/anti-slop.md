# Install the anti-slop oxlint plugin (JS/TS)

[dmmulroy/anti-slop](https://github.com/dmmulroy/anti-slop) is a set of oxlint
rules that reject low-evidence TypeScript and JavaScript patterns, for example
`no-module-mocking` and `no-chained-type-assertions`. It is MIT licensed. It is
not an npm package: a project copies the upstream `src/` into its own tree.

## Steps

1. Copy upstream `src/` into `tools/oxlint/anti-slop/`. Take it from upstream, not from another project; project copies drift.
2. If the project does not use Effect, delete `effect/` and the imports of its rules from `index.ts`.
3. Copy upstream `LICENSE` into the same folder.
4. Add a `README.md` there: the upstream URL, the date you copied it, what you left out, and how to update ("copy `src/` again and rerun the linter").
5. Add `@oxlint/plugins` as a dev dependency, pinned to the same version as `oxlint`.
6. Register the plugin and turn on its rules in `.oxlintrc.json`:

```json
{
  "jsPlugins": [{ "name": "anti-slop", "specifier": "./tools/oxlint/anti-slop/index.ts" }],
  "rules": {
    "complexity": ["error", { "max": 10 }],
    "anti-slop/no-module-mocking": "error",
    "anti-slop/no-chained-type-assertions": "error"
  }
}
```

List every rule the copied `index.ts` exports, each set to `"error"`. Turn a
rule off only with the user's agreement, and record why in the coding standard.

7. Run the linter on the whole project. On a running project, report the violations first; fix them in their own change, not inside the setup.
