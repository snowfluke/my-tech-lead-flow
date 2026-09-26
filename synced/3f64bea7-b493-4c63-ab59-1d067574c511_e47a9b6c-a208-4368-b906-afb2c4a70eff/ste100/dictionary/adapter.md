# Dictionary adapter interface

Implement or invoke an authorized external checker with this logical interface. The adapter must return `approved`, `not-approved`, or `unverified`; it must not copy the dictionary into this repository.

```text
lookup(word, context, requested_part_of_speech) ->
  {
    status: approved | not-approved | unverified,
    approved_part_of_speech: optional,
    approved_forms: optional,
    approved_meaning: optional,
    source_id: required when verified
  }
```

Pass context because ASD approval can depend on meaning and subject field. Cache only if the organization's authorization permits it, and keep any cache outside the skill repository. If the adapter is absent, report `UNVERIFIED` rather than guessing or substituting a self-created word list.
