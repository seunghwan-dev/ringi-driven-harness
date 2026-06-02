# Methodology

> The full workflow. For the field context behind the term *harness*, see [harness-mapping.md](harness-mapping.md).

ringi-driven-harness lets one developer ship production software with Claude doing most of the building — without giving up control of what reaches `main`. The human designs and approves; the cloud builds and verifies.

As agent fleets get cheap, the building stops being the scarce part — governance does: an independent check on the work, a human gate on what merges, and decisions that persist across sessions. This harness is that governance layer, and it sits on top of however the agent happens to run.

## The shift: from in the loop to at the gates

In v1 ([ringi-driven-dev](https://github.com/seunghwan-dev/ringi-driven-dev)), the developer sat at the keyboard and drove Claude Code in real time. It worked, but it was synchronous: no developer, no progress.

v2 is asynchronous. Work is specified as GitHub issues, built autonomously in the cloud, and queued as pull requests. The developer reviews and merges when they are available — in the evening, between meetings, whenever. The machine does not wait for the human to be awake.

The human is no longer *in the loop*, present for every step. The human is *at the gates*, present at the one decision that matters: what ships.

## Operating modes

The shift from synchronous to asynchronous is not a single jump — it is a spectrum. The harness runs in three modes, and they differ only in *where the human stands and how the work is triggered*. All three converge on the same gate.

![operating modes converge on one gate](../diagrams/operating-modes.svg)

- **Synchronous** — the human is at the terminal. Best for exploration and 0→1 work, where a decision branches and each result changes the next move.
- **Remote / dispatch** — the human is in the loop, but remote. A bounded, specified task runs elsewhere and pauses for approval at any consequential step.
- **Autonomous** — the human is out of the loop until review. A schedule or trigger starts the build; it opens a pull request and stops, never merging on its own. Best for well-defined, well-fenced work in the steady state. The mechanism is a scheduled CI job (the bundled nightly workflow) or Claude Code routines (`/schedule`).

Alongside these, **parallel orchestration** — large fan-outs of subagents for audits, multi-angle review, or scale — is a tool any mode can reach for. It belongs to the wide jobs, not the core exploratory loop.

**Convergence.** Every mode ends in the same place: the automated check (CI) runs, an AI review advises (`@claude`), and a human stamps the merge. The mode changes *where the human is and how the work is triggered*; it does not change *what ships or who approves it*.

**The governance-layer thesis.** The cheaper and more trivial the fleet becomes, the more the scarce, durable part is governance — not the building. The harness is that layer, and it is temperament-independent: it rides on top of whichever mode the work runs in.

## The five tiers

1. **HQ chat** — Claude as architect. The developer and HQ design the work and evaluate results. Strategy lives here.
2. **GitHub Issues** — the work queue. Each issue is a self-contained spec: what to build, how to verify it, what done looks like.
3. **Claude Code Routines** — the builder. A full Claude Code session running in Anthropic's cloud, on a schedule or trigger. The developer's machine can be off.
4. **Claude Code GitHub Action** — the responder. Reacts to `@claude` on a pull request to fix or revise, in place.
5. **HQ review** — the gate. The developer and HQ evaluate the pull request and decide whether to merge.

## A task's lifecycle

```
Design (developer + HQ chat)
  → GitHub Issue (self-contained spec)
  → Autonomous build (Routines, in the cloud)
  → Pull Request
  → Automated review + CI
  → HQ review
  → Merge gate (developer approves)
  → main → next task
```

If a change is rejected at the gate, a comment to `@claude` sends it back for revision and re-verification. If approved, it merges and the next task begins.

## Why a self-contained spec matters

A Routine runs in a clean cloud session. It cannot see the HQ conversation that produced the issue. Whatever intent is not written into the issue does not exist for the builder — it gets filled with a plausible guess instead. Every drift this methodology has produced traces back to a spec that omitted an intention the author assumed was obvious. The rule is simple and unforgiving: if it is not in the spec, it did not happen.

## The work order as a safety control

The more asynchronous the oversight — remote, or fully autonomous — the more the work order *is* the primary safety control. When no one is watching the build in real time, the issue spec is what keeps it in bounds: it fixes the scope, names the files it may touch, defines the acceptance and verification, and forbids changes outside the line. A vague work order under autonomy is an agent improvising unsupervised.

A routine's behavior comes down to three decisions, and the work order is where they are pinned down:

- **Trigger** — when the build runs: a schedule, a label, a comment.
- **Context** — what it is allowed to read: the Goal, Intent, and Scope it is given.
- **Steering** — how it is constrained: the Files, Acceptance criteria, and Forbidden actions.

`templates/issue-template.md` is that work order — the canonical form a task takes before it is handed to a build.

## The cross-check, in brief

Up to four independent Claude sessions touch a single change — the one that designs, the one that builds, the one that reviews on the pull request, and the one that evaluates with the developer. None sees the others' conclusions. That mutual blindness is the check: a mistake has to survive four independent looks before it ships. See [harness-mapping.md](harness-mapping.md) for how this maps to verification in harness terms.

## Why the cross-check must be independent

Error detection does not come from a *second person* — it comes from a *second, independent context*. A reviewer that shares the builder's context shares its blind spots: it will confidently miss the same thing. So the check does not require a separate human; it requires separation. A subagent reviewer, `@claude` on the pull request, a fresh session reading the diff cold — each is independent enough to catch what the builder could not see in itself.

Tier the independence to the risk. Routine, low-stakes work can be checked by a reviewer inside the same environment; a high-stakes change — a security boundary, a data path, an irreversible action — is mediated by a human. That is why the AI review gate exists at all: not as a formality before the human, but as the independent reader that keeps the human gate meaningful.

## Where work happens

- **Cloud**, with the developer's machine off: design chat, autonomous build, automated review, CI.
- **Local**, with the developer present: pull-request review, final verification, merge.

The two meet at the GitHub repository, synchronized one pull request at a time.

## Bootstrapping vs steady state

A new repository has no branch protection and no pull-request gate yet, so its first commits are made by the developer directly on `main`. This is bootstrapping, not the steady state. Once the harness is operational — CI, branch protection, Routines — commits move to branches, pull requests appear, and the human gate settles where it belongs: at the merge.

The gate is always the merge. Who makes the commit changes; where the human stands does not.

The human gate does not stand alone. AI-written code can look correct yet fail on an edge case or hide a vulnerability — "looks right" is not "is right." So tests are not optional. Branch protection turns the CI workflow (secret scan, then tests) into a required status check: a pull request that is not green cannot be merged, even by the developer. The automated gate is the precondition; the human gate is the decision.

## Gates at every stage

It is tempting to think of this harness as having a single gate — the human merge. It has
three, and the human holds the last one.

1. **The automated gate.** Every change is checked by CI before it can merge: the test
   suite must pass and a secret scan (gitleaks) must come back clean. This is the `verify`
   status check, and `main` will not accept a merge without it.
2. **The AI review.** `@claude` reviews the change on the pull request — a second reader
   that runs every time, tirelessly, and never gets bored on the fiftieth diff of the day.
   It surfaces issues for the human, but it does not merge.
3. **The human gate.** A person reads the diff and the AI's review, then decides — and
   stamps the merge. This is the ringi.

The layers exist because each covers the others' blind spots. A green CI run is necessary,
not sufficient: tests catch regressions, not bad judgment. An AI reviewer is a tireless
second pair of eyes, but an AI that both writes and reviews shares its own blind spots and
can be confidently wrong — so it advises, it does not decide. A human brings judgment and
accountability, but a human alone tires, rubber-stamps, and cannot read everything
carefully — so the first two layers exist to keep the human gate meaningful rather than a
formality. A mistake has to slip past all three.

**The gate guards only what it runs.** A passing check covers the surfaces it exercises, and no others. A surface the gate never runs — a frontend that compiles but is never rendered, an integration never driven — is an ungated path: it reaches the human green and can still be broken. So coverage is matched to the surfaces a change actually has, and it is layered — lint, type-check, unit, end-to-end — with each layer added as a step inside the required job, never as a separate optional one that sits un-required until someone remembers to register it. The runtime layers especially: a UI's behavior is only real in a running browser, so something has to run it before the human does — a deterministic end-to-end suite in the gate, or an agent with eyes on the page that drives the flow, finds the regression, and turns it into a test the gate then keeps. The human gate is for judgment, not for discovering a broken render by clicking through by hand.

**Severity decides what blocks.** Not every finding is equal. A finding marked *critical*
— a security hole, a data-loss path, a broken contract — blocks the merge until resolved.
An *advisory* finding — a style preference, an unlikely edge case — is left to the human's
judgment at the gate. Critical findings are resolved before the stamp; advisory findings
inform it.

**Why the human keeps the last gate.** The harness could automate the final decision too
— let the AI approve and merge its own work. It deliberately does not. The rule is *the AI
proposes, the human decides*: machines prepare, vet, and recommend; a person reviews and is
accountable for what reaches `main`. That is the ringi. Every layer before the human exists
to make that decision easy and well-informed, not to replace it.

## Progressive adoption

Do not hand over the keys to full autonomy on day one. Trust is built in stages:

1. **Action first** — keep working as before, but call `@claude` on pull requests to get a feel for agent review.
2. **One small Routine** — delegate a single low-risk task, such as a docs update or a test, to an autonomous build.
3. **Full async** — once the output is trustworthy, route feature work through Routines and review the pull requests.

This repository was bootstrapped by hand and is being moved, stage by stage, onto the workflow it describes.
