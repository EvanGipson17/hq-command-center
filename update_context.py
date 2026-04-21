#!/usr/bin/env python3
"""
update_context.py — append a dated entry to EVAN_BUSINESS_CONTEXT.md
and commit + push to GitHub.

Usage:
    python update_context.py "your note here"

From any PowerShell terminal (if the `context` function is in your profile):
    context "your note here"

Behavior:
  1. Opens EVAN_BUSINESS_CONTEXT.md in the hq-command-center repo.
  2. Finds the "## Decisions Log" section.
  3. Appends a new entry in the format:   - **YYYY-MM-DD** — <your note>
     (entries accumulate in chronological order; newest at the bottom).
  4. Commits only that file with message "context: <first 72 chars of note>".
  5. Pushes to origin. If push fails (auth, offline), the local commit
     stays — just run `git push` manually later.

The script exits non-zero on any error so the calling shell sees the failure.
"""
import subprocess
import sys
from datetime import date
from pathlib import Path

# Force UTF-8 on stdout/stderr so em-dashes etc. print cleanly in Windows consoles.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── Config ────────────────────────────────────────────────────────────────
REPO_DIR       = Path(r"C:\Users\wwgip\hq-command-center")
CONTEXT_FILE   = REPO_DIR / "EVAN_BUSINESS_CONTEXT.md"
SECTION_HEADER = "## Decisions Log"


def fail(msg: str) -> None:
    print(f"context: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        fail('usage: context "your note"')
    note = " ".join(sys.argv[1:]).strip()
    if not note:
        fail("empty note")

    if not CONTEXT_FILE.exists():
        fail(f"{CONTEXT_FILE} not found")

    today = date.today().isoformat()  # YYYY-MM-DD
    entry = f"- **{today}** — {note}"

    content = CONTEXT_FILE.read_text(encoding="utf-8")
    if SECTION_HEADER not in content:
        fail(f"'{SECTION_HEADER}' section not found in {CONTEXT_FILE.name}")

    # Insert the new entry at the end of the Decisions Log section,
    # just before the next "## " heading (or EOF if none).
    lines = content.splitlines()
    out: list[str] = []
    i = 0
    appended = False
    while i < len(lines):
        out.append(lines[i])
        if not appended and lines[i].strip() == SECTION_HEADER:
            i += 1
            # Collect the section body until the next ## heading or EOF.
            body: list[str] = []
            while i < len(lines) and not lines[i].startswith("## "):
                body.append(lines[i])
                i += 1
            # Drop any trailing blank lines so the new entry sits tight
            # against the existing list.
            while body and body[-1].strip() == "":
                body.pop()
            body.append(entry)
            body.append("")  # trailing blank line before next section
            out.extend(body)
            appended = True
            continue
        i += 1

    # Preserve original trailing newline behavior if file had one.
    new_content = "\n".join(out)
    if content.endswith("\n") and not new_content.endswith("\n"):
        new_content += "\n"

    CONTEXT_FILE.write_text(new_content, encoding="utf-8")
    print(f"  appended: {entry}")

    # Git: stage only the context file, commit, push.
    commit_msg = f"context: {note[:72]}"
    try:
        subprocess.run(
            ["git", "add", "--", str(CONTEXT_FILE.name)],
            cwd=REPO_DIR, check=True,
        )
        # If nothing changed (re-running with same note), git commit errors.
        # Check for staged changes first.
        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=REPO_DIR,
        )
        if diff.returncode == 0:
            print("  no changes to commit (file already up to date)")
            return

        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=REPO_DIR, check=True,
        )
        print(f"  committed: {commit_msg}")
    except subprocess.CalledProcessError as e:
        fail(f"git commit failed: {e}")

    try:
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        print("  pushed to origin")
    except subprocess.CalledProcessError:
        print(
            "  warning: git push failed (commit is local). "
            "Run `git push` manually when online.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
