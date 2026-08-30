#!/usr/bin/env python3
"""
check_repo_sync.py — is the working tree consistent with git, and git with GitHub?

NOT A PIPELINE STEP. This is a read-only audit: it never stages, commits, pushes,
moves or deletes anything. It prints what it finds and exits non-zero if something
needs attention, so it is safe to run at any time and usable in a pre-push hook.

What it checks
--------------
  * local HEAD against origin/main — commits to push, commits to pull
  * uncommitted and staged changes
  * untracked files, split into "probably junk" and "needs a decision"
  * stray duplicates: a .py in the repo root that also exists in scripts/
  * every pipeline script present and tracked
  * files the analysis depends on that git is ignoring

Usage
-----
    python scripts/check_repo_sync.py
    python scripts/check_repo_sync.py --no-fetch     # skip the network call
"""

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

# Files the analysis depends on. Being gitignored is not automatically wrong —
# large derived data usually should be — but a file that defines the coordinate
# system is worth knowing about.
CRITICAL_INPUTS = [
    ("data/processed/H_clade_3_ref.fasta", "defines the annotation coordinate system"),
    ("data/processed/H_clade_3.fasta", "clade 3 alignment"),
    ("data/processed/metadata_clean.tsv", "metadata joined into the export"),
    ("config/lineage_references.tsv", "lineage reference accessions"),
]

PIPELINE = [
    "00_check_env.py", "01_fetch_sequences.py", "02_curate_metadata.py",
    "03_align_and_tree.py", "04_alignment_qc.py", "05_tree_summary.py",
    "06_subsample.py", "07_make_beast_xml.py", "08_add_references.py",
    "09_make_auspice.py", "10_add_entropy.py", "11_annotate_H.py",
    "cdv_h_coords.py",
]

# Untracked files matching these are scratch, not decisions.
JUNK_SUFFIXES = (".bak.json", ".bak", ".orig", ".rej", ".pyc")
JUNK_NAMES = ("COMMIT_MSG.txt", ".DS_Store")
JUNK_PREFIXES = ("COMMIT_MSG",)


def git(*args, check=True, strip=True):
    """Run git and return stdout.

    strip=False matters for `status --porcelain`, whose first column is a
    meaningful space: stripping it shifts every status code by one and turns an
    unstaged change into a staged one.
    """
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip() if strip else r.stdout.rstrip("\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section(title):
    print(f"\n{title}")
    print("-" * len(title))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-fetch", action="store_true",
                    help="Skip 'git fetch'; compare against the last known remote state")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--branch", default=None, help="Default: the current branch")
    args = ap.parse_args()

    try:
        root = Path(git("rev-parse", "--show-toplevel"))
    except Exception as e:
        print(f"not a git repository: {e}", file=sys.stderr)
        return 2
    print(f"repo:   {root}")

    branch = args.branch or git("rev-parse", "--abbrev-ref", "HEAD")
    print(f"branch: {branch}")

    problems = 0

    # ---- remote ---------------------------------------------------------
    section("GitHub")
    if not args.no_fetch:
        r = subprocess.run(["git", "fetch", args.remote, "--quiet"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  could not fetch ({r.stderr.strip() or 'no network?'});"
                  " comparing against the last known remote state")
    upstream = f"{args.remote}/{branch}"
    has_remote = subprocess.run(["git", "rev-parse", "--verify", "--quiet", upstream],
                                capture_output=True).returncode == 0
    if not has_remote:
        print(f"  no {upstream} — nothing to compare against")
        problems += 1
    else:
        counts = git("rev-list", "--left-right", "--count", f"{upstream}...HEAD")
        behind, ahead = (int(x) for x in counts.split())
        if ahead:
            print(f"  {ahead} commit(s) to push:")
            for line in git("log", "--oneline", f"{upstream}..HEAD").splitlines():
                print(f"    {line}")
            problems += 1
        if behind:
            print(f"  {behind} commit(s) to pull")
            problems += 1
        if not ahead and not behind:
            print("  in sync")

    # ---- working tree ---------------------------------------------------
    section("Working tree")
    staged, modified, untracked = [], [], []
    for line in git("status", "--porcelain=v1", strip=False).splitlines():
        code, path = line[:2], line[3:].strip().strip('"')
        if code == "??":
            untracked.append(path)
        else:
            if code[0] not in " ?":
                staged.append((code[0], path))
            if code[1] not in " ?":
                modified.append((code[1], path))

    if staged:
        print(f"  {len(staged)} staged but uncommitted:")
        for c, p in staged:
            print(f"    [{c}] {p}")
        problems += 1
    if modified:
        print(f"  {len(modified)} modified, not staged:")
        for c, p in modified:
            print(f"    [{c}] {p}")
        problems += 1
    if not staged and not modified:
        print("  clean")

    # ---- untracked ------------------------------------------------------
    if untracked:
        junk = [p for p in untracked
                if p.endswith(JUNK_SUFFIXES) or Path(p).name in JUNK_NAMES
                or Path(p).name.startswith(JUNK_PREFIXES)]
        real = [p for p in untracked if p not in junk]
        section("Untracked")
        if junk:
            print(f"  {len(junk)} scratch file(s), safe to delete:")
            for p in junk:
                print(f"    {p}")
        if real:
            print(f"  {len(real)} file(s) needing a decision — add or delete:")
            for p in real:
                size = (root / p).stat().st_size if (root / p).is_file() else 0
                print(f"    {p}  ({size:,} bytes)")
            problems += 1

    # ---- stray duplicates ------------------------------------------------
    section("Stray copies in the repo root")
    strays = []
    for p in sorted(root.glob("*.py")):
        twin = root / "scripts" / p.name
        if twin.is_file():
            same = digest(p) == digest(twin)
            strays.append((p.name, same))
    if not strays:
        print("  none")
    else:
        for name, same in strays:
            if same:
                print(f"  {name:<24} identical to scripts/{name} — delete the root copy")
            else:
                print(f"  {name:<24} DIFFERS from scripts/{name} — compare before deleting")
                print(f"      diff {name} scripts/{name}")
        problems += 1

    # ---- pipeline completeness -------------------------------------------
    section("Pipeline scripts")
    tracked = set(git("ls-files", "scripts/").splitlines())
    missing, untracked_script = [], []
    for name in PIPELINE:
        rel = f"scripts/{name}"
        if not (root / rel).is_file():
            missing.append(name)
        elif rel not in tracked:
            untracked_script.append(name)
    if missing:
        print(f"  MISSING: {', '.join(missing)}")
        problems += 1
    if untracked_script:
        print(f"  present but not tracked: {', '.join(untracked_script)}")
        problems += 1
    if not missing and not untracked_script:
        print(f"  all {len(PIPELINE)} present and tracked")

    # ---- critical inputs --------------------------------------------------
    section("Analysis inputs")
    for rel, why in CRITICAL_INPUTS:
        path = root / rel
        if not path.is_file():
            print(f"  [{'absent':<8}] {rel}  — {why}")
            continue
        ignored = subprocess.run(["git", "check-ignore", "-q", rel],
                                 capture_output=True).returncode == 0
        state = "ignored" if ignored else ("tracked" if rel in set(
            git("ls-files", rel).splitlines()) else "UNTRACKED")
        print(f"  [{state:<8}] {rel}  — {why}")
        if state == "UNTRACKED":
            problems += 1
    print("\n  'ignored' is fine for large derived data, but anything defining the")
    print("  coordinate system should be reproducible: either track it (git add -f)")
    print("  or record the exact command that regenerates it in the README.")

    # ---- verdict -----------------------------------------------------------
    print()
    if problems == 0:
        print("Everything is committed and pushed.")
        return 0
    print(f"{problems} thing(s) need attention — see above. Nothing was changed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
