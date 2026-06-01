# Issue / task spec template

Copy this for every unit of work handed to an autonomous build. A clean cloud session sees only what is written here — nothing from the conversation that produced it.

This is the **work order**: the canonical, self-contained form a task takes before it is handed to a build. When no one is watching the build in real time, it is the primary safety control — it fixes the scope, names the files, and defines done, so an unsupervised run stays in bounds.

The fields map a routine's three decisions: **context** — what the build may read (Goal, Intent, Scope); **steering** — how it is constrained (Files to create or change, Acceptance criteria, Forbidden actions); and the **trigger** — when it runs, set by how you file or label the issue.

## Goal

One sentence: what this task achieves, and why.

## Intent

The reasoning a reviewer needs to judge whether the result is right. Anything you assume is obvious belongs here — that is exactly what gets lost otherwise, and the gap gets filled with a plausible guess.

## Scope

- In:
- Out:

## Files to create or change

- `path/to/file` —

## Acceptance criteria

- [ ]
- [ ]

## Verification

The exact commands that confirm the criteria, with expected output. For PowerShell reads of UTF-8 files, pass `-Encoding UTF8`.

## Forbidden actions

- No `git commit` / `push` unless stated here.
- (project-specific guardrails)

## Done looks like

A short description of the finished state, and the completion-report format expected back.
