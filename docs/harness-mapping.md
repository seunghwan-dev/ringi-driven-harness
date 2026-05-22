# What this is, in harness-engineering terms

> Companion to [methodology.md](methodology.md).

## What a harness is

An *agent harness* is the scaffolding around a model that turns it into a working agent: the execution loop, the tools it can call, how its context is managed, the guardrails on what it may do, and the verification that catches its mistakes. A useful shorthand is **Agent = Model + Harness**. Every part of a harness encodes an assumption about what the model cannot be trusted to do on its own.

Most discussion of harnesses is about the *inner* harness — the code immediately wrapping the model, such as a coding agent's own loop and tool dispatch. ringi-driven-harness is an *outer* harness, or *user harness*: the scaffolding a developer builds around the agent — issues, gates, reviews, CI — to steer it across many sessions. Building a user harness is a form of context engineering, and the developer's real job is to keep improving the harness: when a failure recurs, you add the control that prevents it.

## How the pieces map

| In this repository | In harness terms |
|---|---|
| `CLAUDE.md` rules | Guardrails / safety enforcement |
| Self-contained issue spec | Context management |
| CI (gitleaks, tests, Playwright) | Verification / error recovery |
| Four-session cross-check | Self-correction loop |
| Human merge gate | Human steering layer |
| Claude Code Routines | Execution loop / orchestration |

## The two names

This methodology carries two names on purpose.

- **ringi-driven** is the cultural frame. *Ringi* (稟議) is the Japanese practice of circulating a proposal for approval before acting. It captures the one rule that never bends here: nothing reaches `main` without a human approving it. *Human at the gates.*
- **harness engineering** is the technical category. It is how the field names this work, and it makes the methodology legible to anyone building with agents, anywhere.

The same system, described to two audiences.

## The harness improves itself

A harness is never finished. Each failure is a missing control:

- A spec that omitted the author's intent let the builder invent its own. The fix: the issue template now demands explicit intent.
- A verification command misread a UTF-8 file under a non-UTF-8 locale and reported a defect that was not there. The fix: measurements now pin their encoding, and a rule was added — when a result looks wrong, suspect the instrument before the artifact.

These are not hypotheticals; they happened while building this repository. The accumulated controls live in `templates/` as reusable guardrails.
