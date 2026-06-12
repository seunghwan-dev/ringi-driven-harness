# <PROJECT>

A [ringi-driven-harness](https://github.com/seunghwan-dev/ringi-driven-harness) project:
built autonomously, with a human at the gate. Nothing reaches `main` without a human's
review and merge.

## The gate

Every change flows the same way:

```
branch -> commit -> push -> pull request -> CI (verify) -> @claude review -> human merge
```

- Direct pushes to `main` are blocked by branch protection.
- The `verify` status check (secret scan, plus your stack's checks on an app profile) must be
  green before a merge.
- `@claude` review is **owner-triggered**: mention `@claude` on a pull request (as OWNER /
  MEMBER / COLLABORATOR) to request the review. It does not run automatically.

## Guardrails

[CLAUDE.md](CLAUDE.md) holds the rules every autonomous and assisted change must follow.
File each unit of work as a self-contained work order using
[templates/issue-template.md](templates/issue-template.md).

## Methodology

Governed by the ringi-driven-harness methodology — read it before you build:
https://github.com/seunghwan-dev/ringi-driven-harness/blob/main/docs/methodology.md
