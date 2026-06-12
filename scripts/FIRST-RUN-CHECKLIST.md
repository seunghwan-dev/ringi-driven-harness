# First-run checklist

A new repository is **harness-ready** when all six items below pass. Replace `<OWNER>/<REPO>`
with the new repository (for example `seunghwan-dev/my-project`) and `<PR#>` / `<ID>` with the
real values. Most checks use `gh`; run them from anywhere you are authenticated (`gh auth
status`).

`scripts/init_harness_repo.py` performs items 1-3 automatically — item 3 only if the
`CLAUDE_CODE_OAUTH_TOKEN` environment variable was set when it ran. Items 4-6 are a live,
end-to-end proof that the gate actually works; do them by hand once per new repo.

## 1. Repo created + scaffold pushed to main

```
gh repo view <OWNER>/<REPO> --json name,visibility,defaultBranchRef
gh api repos/<OWNER>/<REPO>/contents/.github/workflows/verify.yml --jq .name
gh api repos/<OWNER>/<REPO>/contents/.github/workflows/claude.yml --jq .name
gh api repos/<OWNER>/<REPO>/contents/CLAUDE.md --jq .name
```
Pass: the repo exists with default branch `main`, and each file resolves to its name.

## 2. Branch-protection ruleset active

```
gh api repos/<OWNER>/<REPO>/rulesets --jq '.[] | {name, enforcement}'
gh api repos/<OWNER>/<REPO>/rulesets/<ID> --jq '.rules[].type'
```
Pass: a ruleset named `protect-main` is `active`, and its rules include `pull_request`,
`required_status_checks` (context `verify`), `deletion`, and `non_fast_forward`. A direct
`git push` to `main` is rejected.

## 3. Claude OAuth secret set

```
gh secret list --repo <OWNER>/<REPO>
```
Pass: `CLAUDE_CODE_OAUTH_TOKEN` is listed. If the bootstrap skipped it, set it now and paste
the token at the prompt — never on the command line:
```
gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo <OWNER>/<REPO>
```

## 4. Trivial test PR -> CI `verify` runs and is green

```
# from a fresh clone of the new repo
git switch -c test/harness-smoke
# make a trivial change, e.g. add a line to README.md
git commit -am "Smoke-test the gate"
git push -u origin test/harness-smoke
gh pr create --fill
gh pr checks --watch
```
Pass: the `verify` check runs on the pull request and finishes green.

## 5. @claude mention on the test PR -> review posts

```
gh pr comment <PR#> --body "@claude please review"
```
Pass: within a few minutes the Claude Code action runs and posts a review comment. You must
comment as OWNER / MEMBER / COLLABORATOR — the workflow ignores everyone else.

## 6. Claude Code can branch, edit, commit, push

```
# In a Claude Code session pointed at the new repo, ask it to make a small change on a
# branch and push it. Then confirm a direct push to main is refused:
git push origin HEAD:main   # expect: rejected by branch protection
```
Pass: Claude Code creates a branch, commits, and pushes it; the direct push to `main` is
blocked by branch protection.

---

When all six pass, close the test pull request (or merge it through the gate as the first real
ringi stamp) and delete the smoke-test branch. The repo is harness-ready.
