# ringi-driven-harness

> A human-at-the-gates harness for Claude. Coding agents build production software — beside you, while you're away, or while you sleep — and every change converges on one gate where a human keeps final control over what ships. As agent fleets get cheap, this governance layer is the scarce part.

**English** · [日本語](README.ja.md)

## What this is

ringi-driven-harness is a methodology — a *user harness* for building real software with Claude Code. It defines how a single developer orchestrates autonomous coding agents through GitHub, with a human approval gate (稟議, *ringi*) in front of every change that reaches `main`.

It is the evolution of [ringi-driven-dev](https://github.com/seunghwan-dev/ringi-driven-dev). v1 was synchronous — you sat at the keyboard. v2 is asynchronous — the work runs in the cloud while you are at the office or asleep, and you review the results when you return.

## Why it exists

Coding agents can now build entire features on their own. Left unsupervised, they also drift from intent, mistake the scope, and ship UI that does not work. The question is no longer *can the agent build it* — it is *how does a human stay in control without sitting in the loop all day*.

A harness answers that. An agent harness is the scaffolding around a model — the execution loop, tools, context management, guardrails, and verification — that turns a raw model into a reliable agent. This repository is a harness at the *workflow* level: the human designs and approves; the cloud builds and verifies.

As agents get cheaper and faster, the fleet stops being the constraint. What stays scarce is governance: an independent check on the work, a human gate on what merges, and decisions that hold across sessions. This harness is that governance layer — and it rides on top of any way the agent runs, whether you drive it yourself, dispatch it remotely, or let it work on a schedule.

## The workflow

![ringi-driven-harness workflow](diagrams/workflow.svg)

Four independent Claude sessions touch each change — the one that designs, the one that builds, the one that reviews, the one that evaluates — and none of them sees the others' conclusions. That mutual blindness is the cross-check.

The merge gate is the heart of the harness: everything above it can be automated, but whether a change ships is one human click. That click sits behind an automated gate: tests and a secret scan run as required checks, so a change that is not green never reaches it. That is *human at the gates, not in the loop*.

The diagram above is the steady-state path, where the build runs in the cloud while you are away. But the human can stand in different places without moving the gate. The work runs in one of three modes — **synchronous** (you drive the agent at the terminal), **remote dispatch** (a bounded task you hand off to run while you are away), or **autonomous** (a schedule or trigger builds and opens a pull request, then stops) — and all three converge on the same gate.

![operating modes converge on one gate](diagrams/operating-modes.svg)

The mode changes *where the human stands and how the work is triggered*; it does not change *what ships or who approves it*. For the full treatment, see [the methodology](docs/methodology.md#operating-modes).

## Repository layout

```
docs/        Methodology, written as a user harness
diagrams/    SVG visualizations of the workflow
templates/   Reusable harness components (CLAUDE.md, issue template, CI)
```

## Lineage

- **v1** [`ringi-driven-dev`](https://github.com/seunghwan-dev/ringi-driven-dev) — synchronous. Human at the keyboard.
- **v2** `ringi-driven-harness` — asynchronous harness. Autonomous builds that open pull requests for review.

## Status

Work in progress. This repository is built using the workflow it describes.

## Related work

This harness draws on written practice from the broader Claude Code / agentic-development community, adapted to its own human-at-the-gates philosophy:

- [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — the implementer-discipline principles (think before coding, simplicity, surgical changes, goal-driven execution) build on its distillation of common LLM coding pitfalls.
- [ECC](https://github.com/affaan-m/ECC) — grading review findings by severity (what blocks vs. what merely informs) is adapted from its security-review and verification practice; its end-to-end testing agent also informs the stance that a runnable surface is gated by running it, not by reading it.
- [gstack](https://github.com/garrytan/gstack) — the "the AI proposes, the human decides" framing of bounded autonomy echoes its builder ethos; its QA agent that drives a real browser and turns each bug it finds into a regression test is the prior art for putting eyes on the running UI before the human does.

Where those projects largely automate the review gates, this harness keeps a human at the final gate by design — the ringi stamp. The pieces are borrowed as written norms only; none of their runtime systems (skill packs, hooks, agents) are vendored here. All three are MIT-licensed; the principles above are adapted in our own words, not copied.

## License

[MIT](LICENSE)
