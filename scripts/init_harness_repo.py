#!/usr/bin/env python3
"""init_harness_repo.py - one-shot bootstrap for a ringi-driven-harness repo.

Creates a new GitHub repository configured to harness standards in a single command:

  * scaffolds the verify CI + @claude review workflows, CLAUDE.md, .gitignore,
    README, and the work-order issue template (profile-aware)
  * commits and pushes the scaffold to main
  * applies the branch-protection ruleset (pull request required, `verify`
    required status check, direct push to main blocked)
  * sets the Claude OAuth secret from the environment - never from a literal

To avoid duplicating content, the tool reuses this harness checkout's own canonical
files (CLAUDE.md, the issue template, .gitignore, the @claude workflow) and copies the
two verify.yml variants and the README skeleton from scripts/scaffold/. It must therefore
be run from inside a checkout of the harness repo. See scripts/README.md.

Usage:
    python scripts/init_harness_repo.py <repo-name> [--profile docs|app] [--public] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCAFFOLD_DIR = SCRIPT_DIR / "scaffold"

SECRET_NAME = "CLAUDE_CODE_OAUTH_TOKEN"
RULESET_NAME = "protect-main"
DEFAULT_BRANCH = "main"
STATUS_CHECK_CONTEXT = "verify"
# GitHub Actions' app id; pins the required `verify` check to Actions (matches this repo).
GITHUB_ACTIONS_INTEGRATION_ID = 15368
COMMIT_MESSAGE = "Bootstrap harness repository"

# Canonical files reused verbatim from this harness checkout, so nothing is duplicated under
# scaffold/. Maps source path (relative to the harness repo root) -> path in the new repo.
REUSED_FILES = {
    "templates/CLAUDE.md": "CLAUDE.md",
    "templates/issue-template.md": "templates/issue-template.md",
    ".gitignore": ".gitignore",
    ".github/workflows/claude.yml": ".github/workflows/claude.yml",
}


# --- output helpers ---------------------------------------------------------

def step(msg: str) -> None:
    print(f"==> {msg}")


def info(msg: str) -> None:
    print(f"    {msg}")


def planned(msg: str) -> None:
    print(f"    [dry-run] would {msg}")


def warn(msg: str) -> None:
    print(f"!!  {msg}")


def die(msg: str, code: int = 1) -> "None":
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


# --- process helper ---------------------------------------------------------

def run(cmd, *, capture: bool = False, check: bool = True, stdin: str | None = None):
    """Run a command (no shell). Dies with a clean message on failure when check is set."""
    # Decode captured output as UTF-8 regardless of the system locale: gh emits UTF-8
    # (check marks, dashes) and the default locale codec (e.g. cp949) would crash on it.
    try:
        proc = subprocess.run(cmd, capture_output=capture, encoding="utf-8", errors="replace", input=stdin)
    except FileNotFoundError:
        die(f"command not found: {cmd[0]} (is it installed and on PATH?)")
    if check and proc.returncode != 0:
        detail = ((proc.stderr or proc.stdout or "").strip()) if capture else ""
        die(f"command failed ({proc.returncode}): {' '.join(cmd)}" + (f"\n{detail}" if detail else ""))
    return proc


# --- preflight --------------------------------------------------------------

def gh_login() -> str:
    proc = run(["gh", "auth", "status"], capture=True, check=False)
    if proc.returncode != 0:
        die("gh is not authenticated. Run: gh auth login\n" + (proc.stderr or proc.stdout or "").strip())
    proc = run(["gh", "api", "user", "--jq", ".login"], capture=True, check=False)
    login = proc.stdout.strip()
    if proc.returncode != 0 or not login:
        die("could not resolve your GitHub login (gh api user).")
    return login


def repo_exists(full: str) -> bool:
    return run(["gh", "repo", "view", full], capture=True, check=False).returncode == 0


def validate_sources(profile: str):
    """Confirm every source file exists; fail clearly if not run from a harness checkout."""
    missing = [str(REPO_ROOT / src) for src in REUSED_FILES if not (REPO_ROOT / src).is_file()]
    verify_src = SCAFFOLD_DIR / f"verify.{profile}.yml"
    readme_src = SCAFFOLD_DIR / "README.md"
    missing += [str(p) for p in (verify_src, readme_src) if not p.is_file()]
    if missing:
        die("missing source files - run this from a harness checkout:\n  " + "\n  ".join(missing))
    return verify_src, readme_src


# --- scaffold ---------------------------------------------------------------

def compute_files(name: str, verify_src: Path, readme_src: Path) -> dict[str, bytes]:
    """Read every source (read-only) and return {dest path in new repo: bytes}."""
    files: dict[str, bytes] = {}
    for src, dst in REUSED_FILES.items():
        files[dst] = (REPO_ROOT / src).read_bytes()
    files[".github/workflows/verify.yml"] = verify_src.read_bytes()
    readme = readme_src.read_text(encoding="utf-8").replace("<PROJECT>", name)
    files["README.md"] = readme.encode("utf-8")  # UTF-8, no BOM
    return files


def write_files(workdir: Path, files: dict[str, bytes]) -> None:
    for dst, data in files.items():
        target = workdir / dst
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)  # bytes -> exact content, no BOM, no newline translation


# --- git / gh state-changing steps ------------------------------------------

def git_init_commit(workdir: Path) -> None:
    step("Initialize local repository and commit the scaffold")
    run(["git", "-C", str(workdir), "init", "-b", DEFAULT_BRANCH], capture=True)
    run(["git", "-C", str(workdir), "add", "-A"], capture=True)
    run(["git", "-C", str(workdir), "commit", "-m", COMMIT_MESSAGE], capture=True)


def create_and_push(name: str, visibility: str, workdir: Path) -> None:
    step(f"Create {visibility} GitHub repo '{name}' and push to {DEFAULT_BRANCH}")
    run(["gh", "repo", "create", name, f"--{visibility}",
         "--source", str(workdir), "--remote", "origin", "--push"])


def ruleset_payload() -> dict:
    """Branch-protection ruleset matching this repo's `protect-main`."""
    return {
        "name": RULESET_NAME,
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {
                "required_approving_review_count": 0,
                "dismiss_stale_reviews_on_push": False,
                "require_code_owner_review": False,
                "require_last_push_approval": False,
                "required_review_thread_resolution": False,
                "allowed_merge_methods": ["merge", "squash", "rebase"],
            }},
            {"type": "required_status_checks", "parameters": {
                "strict_required_status_checks_policy": False,
                "do_not_enforce_on_create": False,
                "required_status_checks": [
                    {"context": STATUS_CHECK_CONTEXT,
                     "integration_id": GITHUB_ACTIONS_INTEGRATION_ID},
                ],
            }},
        ],
    }


def apply_ruleset(full: str) -> None:
    step(f"Apply branch-protection ruleset '{RULESET_NAME}' "
         f"(PR required, '{STATUS_CHECK_CONTEXT}' required, direct push to {DEFAULT_BRANCH} blocked)")
    run(["gh", "api", "--method", "POST", f"repos/{full}/rulesets", "--input", "-"],
        stdin=json.dumps(ruleset_payload()), capture=True)


def set_secret(full: str) -> None:
    step(f"Set Claude OAuth secret '{SECRET_NAME}'")
    token = os.environ.get(SECRET_NAME)
    if token:
        # Pass the value via stdin so it never appears in argv, logs, or this output.
        run(["gh", "secret", "set", SECRET_NAME, "--repo", full], stdin=token, capture=True)
        info(f"{SECRET_NAME} set from the environment (value not shown).")
    else:
        warn(f"{SECRET_NAME} is not set in the environment - skipping.")
        info("Set it yourself (you will be prompted; the value is not echoed):")
        info(f"  gh secret set {SECRET_NAME} --repo {full}")


# --- dry-run plan -----------------------------------------------------------

def print_plan(full: str, visibility: str) -> None:
    step("Planned actions (dry-run - nothing is created or changed):")
    planned(f"create {visibility} repo {full}")
    planned(f"commit the scaffold and push to {DEFAULT_BRANCH} (normal push)")
    planned(f"create ruleset '{RULESET_NAME}': PR required, required status check "
            f"'{STATUS_CHECK_CONTEXT}', block direct push to {DEFAULT_BRANCH}")
    if os.environ.get(SECRET_NAME):
        planned(f"set secret {SECRET_NAME} from the environment (value never shown)")
    else:
        planned(f"SKIP secret {SECRET_NAME} ({SECRET_NAME} not set) and print the manual "
                f"`gh secret set` command")
    info("then point you to scripts/FIRST-RUN-CHECKLIST.md")


# --- main -------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        prog="init_harness_repo.py",
        description="One-shot bootstrap for a ringi-driven-harness GitHub repo.",
    )
    p.add_argument("repo_name", help="name of the new repository (created under your gh account)")
    p.add_argument("--profile", choices=["docs", "app"], default="docs",
                   help="docs = secret scan only; app = secret scan + stack placeholder (default: docs)")
    p.add_argument("--public", action="store_true", help="make the new repo public (default: private)")
    p.add_argument("--dry-run", action="store_true", help="print the plan; create or change nothing")
    return p.parse_args()


def main() -> None:
    # Relayed gh/git error text may contain non-ASCII; keep the console's encoding but never
    # let an unencodable byte crash our own output on a locale console (e.g. Windows cp949).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except (AttributeError, ValueError):
            pass

    args = parse_args()
    name = args.repo_name
    visibility = "public" if args.public else "private"
    dry = args.dry_run

    step(f"Bootstrap '{name}'  (profile={args.profile}, visibility={visibility}, dry-run={dry})")

    # Preflight (read-only - runs in both modes so a dry-run is a true rehearsal).
    owner = gh_login()
    full = f"{owner}/{name}"
    verify_src, readme_src = validate_sources(args.profile)
    if repo_exists(full):
        if dry:
            warn(f"{full} already exists - a real run would abort here (never overwrites).")
        else:
            die(f"{full} already exists. Refusing to overwrite. Choose another name.")

    files = compute_files(name, verify_src, readme_src)
    step(f"Scaffold for {full} ({len(files)} files):")
    for dst in sorted(files):
        info(f"+ {dst}")

    if dry:
        print_plan(full, visibility)
        return

    workdir = Path(tempfile.mkdtemp(prefix=f"harness-{name}-"))
    write_files(workdir, files)
    git_init_commit(workdir)
    create_and_push(name, visibility, workdir)
    # The repo now exists on main. If configuration fails past this point, a same-name
    # re-run is refused (never overwrites), so surface how to finish it by hand.
    try:
        apply_ruleset(full)
        set_secret(full)
    except SystemExit:
        warn(f"{full} was created and pushed, but configuration did not finish.")
        info("Re-running this tool will refuse (the repo now exists). Finish it by hand:")
        info("  - apply branch protection + set the secret: scripts/FIRST-RUN-CHECKLIST.md items 2-3")
        info(f"  - or remove the half-configured repo and start over: gh repo delete {full}")
        raise

    step("Done - harness repo bootstrapped")
    info(f"Repository: https://github.com/{full}")
    info(f"Local scaffold staged at: {workdir}")
    info(f"  (safe to delete; for a working copy run: gh repo clone {full})")
    info("Next: walk scripts/FIRST-RUN-CHECKLIST.md to confirm the repo is harness-ready.")


if __name__ == "__main__":
    main()
