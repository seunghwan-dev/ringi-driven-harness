# scripts/ — harness repo bootstrap

One-shot tooling to stand up a new GitHub repository configured to ringi-driven-harness
standards, plus the chat-side templates to spin up its HQ.

## What it does

`init_harness_repo.py` creates a new repo and configures it end to end in one command:

1. **Scaffolds** the standard files (profile-aware) — see *Layout* below.
2. **Commits and pushes** them to `main`.
3. **Applies branch protection** — a `protect-main` ruleset requiring a pull request, the
   `verify` status check, and blocking direct pushes to `main`.
4. **Sets the Claude OAuth secret** — read from the environment, never from a literal.

It reproduces *this* harness repo's real configuration: the gitleaks `verify` CI, the
owner-gated `@claude` review workflow, the `protect-main` ruleset, and the
`CLAUDE_CODE_OAUTH_TOKEN` secret.

## Usage

Run from a checkout of the harness repo (the tool reuses this repo's own files — see *Layout*):

```
python scripts/init_harness_repo.py <repo-name> [--profile docs|app] [--public] [--dry-run]
```

| Flag | Default | Meaning |
| --- | --- | --- |
| `<repo-name>` | — | Name of the new repo, created under your `gh` account. |
| `--profile` | `docs` | `docs` = secret scan only. `app` = secret scan + a commented placeholder for your stack's lint / type-check / tests. |
| `--public` | private | Make the new repo public. |
| `--dry-run` | off | Print every action it would take; create or change nothing. |

Always start with `--dry-run` to read the plan.

> **Targets github.com under your own account.** The required-check pin (`integration_id`
> `15368`, the GitHub Actions app) and `gh repo create`'s default owner are github.com-specific.
> On GitHub Enterprise Server the Actions app id differs, which would leave the `verify` check
> unsatisfiable; creating under an organization is also out of scope.

### The Claude secret (safety-first)

The tool sets the `CLAUDE_CODE_OAUTH_TOKEN` repo secret **only** by reading the environment
variable of the same name. It never takes the value on the command line, never echoes it, and
never logs it. Set it for the duration of the command and let the tool read it:

```
# PowerShell
$env:CLAUDE_CODE_OAUTH_TOKEN = "<your-token>"; python scripts/init_harness_repo.py <name>

# bash
CLAUDE_CODE_OAUTH_TOKEN="<your-token>" python scripts/init_harness_repo.py <name>
```

If the variable is not set, the tool **skips** the secret and prints the exact `gh secret set`
command for you to run by hand — which reads the value from a prompt, not the command line.

## Two-step bootstrap

1. **Repo** — run `init_harness_repo.py` to create and configure the GitHub repo.
2. **Chat HQ** — open a new architect chat and paste `templates/PROJECT-HQ-CHARTER.md` (fill the
   `<PLACEHOLDER>`s first). That charter points the chat at the public methodology and this
   checklist, so spinning up a project's HQ is paste-and-go.

Then walk `FIRST-RUN-CHECKLIST.md` to confirm the new repo is harness-ready.

## Layout

```
scripts/
  init_harness_repo.py      the bootstrap tool
  README.md                 this file
  FIRST-RUN-CHECKLIST.md    the six checks a new repo passes to be harness-ready
  scaffold/                 new files the tool copies into a new repo
    verify.docs.yml         verify CI — secret scan only (docs profile)
    verify.app.yml          verify CI — secret scan + stack placeholder (app profile)
    README.md               new-repo README skeleton (<PROJECT> is filled in)
  templates/
    PROJECT-HQ-CHARTER.md   chat-side charter to spin up a project's HQ
```

To avoid duplicating content, the tool **reuses this repo's own canonical files** for the parts
the harness already defines once — it copies `templates/CLAUDE.md`, `templates/issue-template.md`,
the root `.gitignore`, the root `.gitattributes`, and `.github/workflows/claude.yml` straight into
the new repo. Only the files that have no canonical form here (the two `verify.yml` variants and the
README skeleton) live under `scaffold/`. That is why the tool must be run from inside a harness
checkout.
