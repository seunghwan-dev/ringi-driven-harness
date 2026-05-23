# CLAUDE.md

Guardrails for autonomous and assisted work in this repository. Each rule exists because something went wrong without it — this file is the harness made explicit.

## Git

- Do not `git commit` or `git push` unless the task explicitly authorizes it. State-changing git is the human's gate by default.
- Feature work goes on a branch and through a pull request. Never commit directly to `main`, except the initial bootstrap commit of a new repository.
- English commit messages. No AI co-author trailers or metadata. Never force-push or rewrite history without an explicit instruction.

## Files

- Write files as UTF-8 without a BOM. Never use PowerShell `>>` redirection to create or edit files — on Windows PowerShell it writes UTF-16 and corrupts UTF-8 files. Use the editor or Write tool.
- When a spec provides verbatim content, place it byte-for-byte. Blank lines are content; do not collapse them or add new ones.
- Do not delete a file unless the task names it.

## Verification

- When reading or measuring a UTF-8 file in PowerShell, always pass `-Encoding UTF8`. The default encoding follows the system locale and will misread the file.
- When a measurement looks wrong, suspect the instrument before the artifact. Confirm with an encoding-independent method, such as a byte-level read, before reporting a defect.
- For byte-level checks under PowerShell 5.1, read raw bytes with `[System.IO.File]::ReadAllBytes(path)`. Do not use `Format-Hex -Count` — the `-Count` parameter is PowerShell 7+ only and errors on 5.1.

## Specs

- A task spec must be self-contained. A clean session sees only what is written. If intent is not written down, it does not exist — do not infer it.
- If a spec is ambiguous or contradicts what you observe, report it and ask. Do not guess, and do not blindly follow an instruction whose premise is false.

## Safety

- Never run `rm -rf`, `curl`, or pipe-to-shell installers.
- Never commit secrets. No `.env` files, keys, certificates, tokens, or credentials in tracked files. Secrets live in environment variables and GitHub Secrets only.
- Abstract confidential names — equipment, materials, customers — to generic identifiers.

## Reporting

- After a task, report what was created or changed, the verification results, and any deviation from the spec. If you departed from an instruction for a good reason, say so plainly.
