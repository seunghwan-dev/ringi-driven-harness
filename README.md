# ringi-driven-harness

> A human-at-the-gates harness for Claude — coding agents build production software autonomously, even while you sleep, while a human keeps final control over everything that ships.

**English** · [日本語](README.ja.md)

## What this is

ringi-driven-harness is a methodology — a *user harness* for building real software with Claude Code. It defines how a single developer orchestrates autonomous coding agents through GitHub, with a human approval gate (稟議, *ringi*) in front of every change that reaches `main`.

It is the evolution of [ringi-driven-dev](https://github.com/seunghwan-dev/ringi-driven-dev). v1 was synchronous — you sat at the keyboard. v2 is asynchronous — the work runs in the cloud while you are at the office or asleep, and you review the results when you return.

## Why it exists

Coding agents can now build entire features on their own. Left unsupervised, they also drift from intent, mistake the scope, and ship UI that does not work. The question is no longer *can the agent build it* — it is *how does a human stay in control without sitting in the loop all day*.

A harness answers that. An agent harness is the scaffolding around a model — the execution loop, tools, context management, guardrails, and verification — that turns a raw model into a reliable agent. This repository is a harness at the *workflow* level: the human designs and approves; the cloud builds and verifies.

## The workflow

![ringi-driven-harness workflow](diagrams/workflow.svg)

Four independent Claude sessions touch each change — the one that designs, the one that builds, the one that reviews, the one that evaluates — and none of them sees the others' conclusions. That mutual blindness is the cross-check.

The merge gate is the heart of the harness: everything above it can be automated, but whether a change ships is one human click. That click sits behind an automated gate: tests and a secret scan run as required checks, so a change that is not green never reaches it. That is *human at the gates, not in the loop*.

## Repository layout

```
docs/        Methodology, written as a user harness
diagrams/    SVG visualizations of the workflow
templates/   Reusable harness components (CLAUDE.md, issue template, CI)
```

## Lineage

- **v1** [`ringi-driven-dev`](https://github.com/seunghwan-dev/ringi-driven-dev) — synchronous. Human at the keyboard.
- **v2** `ringi-driven-harness` — asynchronous harness. Builds while you sleep.

## Status

Work in progress. This repository is built using the workflow it describes.

## License

[MIT](LICENSE)
