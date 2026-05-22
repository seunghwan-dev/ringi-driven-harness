# Issue / task spec template

Copy this for every unit of work handed to an autonomous build. A clean cloud session sees only what is written here — nothing from the conversation that produced it.

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
