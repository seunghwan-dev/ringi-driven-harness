# Methodology

> The full workflow. For the field context behind the term *harness*, see [harness-mapping.md](harness-mapping.md).

ringi-driven-harness lets one developer ship production software with Claude doing most of the building — without giving up control of what reaches `main`. The human designs and approves; the cloud builds and verifies.

## The shift: from in the loop to at the gates

In v1 ([ringi-driven-dev](https://github.com/seunghwan-dev/ringi-driven-dev)), the developer sat at the keyboard and drove Claude Code in real time. It worked, but it was synchronous: no developer, no progress.

v2 is asynchronous. Work is specified as GitHub issues, built autonomously in the cloud, and queued as pull requests. The developer reviews and merges when they are available — in the evening, between meetings, whenever. The machine does not wait for the human to be awake.

The human is no longer *in the loop*, present for every step. The human is *at the gates*, present at the one decision that matters: what ships.

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

## The cross-check, in brief

Up to four independent Claude sessions touch a single change — the one that designs, the one that builds, the one that reviews on the pull request, and the one that evaluates with the developer. None sees the others' conclusions. That mutual blindness is the check: a mistake has to survive four independent looks before it ships. See [harness-mapping.md](harness-mapping.md) for how this maps to verification in harness terms.

## Where work happens

- **Cloud**, with the developer's machine off: design chat, autonomous build, automated review, CI.
- **Local**, with the developer present: pull-request review, final verification, merge.

The two meet at the GitHub repository, synchronized one pull request at a time.

## Bootstrapping vs steady state

A new repository has no branch protection and no pull-request gate yet, so its first commits are made by the developer directly on `main`. This is bootstrapping, not the steady state. Once the harness is operational — CI, branch protection, Routines — commits move to branches, pull requests appear, and the human gate settles where it belongs: at the merge.

The gate is always the merge. Who makes the commit changes; where the human stands does not.

## Progressive adoption

Do not hand over the keys to full autonomy on day one. Trust is built in stages:

1. **Action first** — keep working as before, but call `@claude` on pull requests to get a feel for agent review.
2. **One small Routine** — delegate a single low-risk task, such as a docs update or a test, to an autonomous build.
3. **Full async** — once the output is trustworthy, route feature work through Routines and review the pull requests.

This repository was bootstrapped by hand and is being moved, stage by stage, onto the workflow it describes.
