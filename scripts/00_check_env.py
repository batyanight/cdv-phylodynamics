#!/usr/bin/env python3
"""
00_check_env.py — verify the environment before you start.

Reports which Python packages, command-line tools and Java applications are
available, and prints the exact command to fix anything missing. Run it after
setup and any time something behaves oddly.

    python scripts/00_check_env.py
"""

import importlib.util
import platform
import shutil
import subprocess
import sys
from pathlib import Path

OK, MISS, WARN = "  OK   ", "MISSING", " NOTE  "

PY_PACKAGES = {
    "Bio": ("biopython", "required", "parsing GenBank records"),
    "pandas": ("pandas", "required", "metadata tables"),
    "matplotlib": ("matplotlib", "required", "plots"),
    "numpy": ("numpy", "required", "numerics"),
    "jupyterlab": ("jupyterlab", "optional", "notebook interface"),
}

BINARIES = {
    "mafft": ("required from phase 3", "sequence alignment"),
    "iqtree2": ("required from phase 3", "maximum likelihood trees"),
    "iqtree": ("alternative to iqtree2", "maximum likelihood trees"),
    "trimal": ("optional", "alignment trimming"),
    "seqkit": ("optional", "FASTA utilities"),
    "hyphy": ("required from phase 4", "selection analysis"),
    "java": ("required from phase 4", "BEAST2, Tracer, TempEst"),
    "git": ("required", "version control"),
}


def check_python_packages():
    print("Python packages")
    print(f"  interpreter: {sys.executable}")
    print(f"  version    : {platform.python_version()}\n")
    missing_required, missing_optional = [], []
    for mod, (pip_name, need, why) in PY_PACKAGES.items():
        present = importlib.util.find_spec(mod) is not None
        status = OK if present else (MISS if need == "required" else WARN)
        print(f"  [{status}] {pip_name:<14} {why}")
        if not present:
            (missing_required if need == "required" else missing_optional).append(pip_name)
    return missing_required, missing_optional


def check_binaries():
    print("\nCommand-line tools")
    missing = []
    have_iqtree = False
    for tool, (need, why) in BINARIES.items():
        path = shutil.which(tool)
        if tool in ("iqtree", "iqtree2") and path:
            have_iqtree = True
        if path:
            print(f"  [{OK}] {tool:<14} {why}")
        elif tool == "iqtree" and have_iqtree:
            continue
        else:
            print(f"  [{MISS if 'required' in need else WARN}] {tool:<14} {why}  ({need})")
            missing.append(tool)
    if have_iqtree:
        missing = [m for m in missing if m not in ("iqtree", "iqtree2")]
    return missing


def check_java():
    if not shutil.which("java"):
        return None
    try:
        out = subprocess.run(["java", "-version"], capture_output=True, text=True)
        return (out.stderr or out.stdout).splitlines()[0]
    except Exception:
        return None


def check_repo():
    print("\nRepository")
    root = Path.cwd()
    while not (root / "scripts" / "02_curate_metadata.py").is_file() and root != root.parent:
        root = root.parent
    if not (root / "scripts" / "02_curate_metadata.py").is_file():
        print(f"  [{MISS}] not inside the repo — cd into cdv-phylodynamics first")
        return None
    print(f"  [{OK}] repo root: {root}")
    for sub in ("scripts", "config", "notebooks", "data/raw", "data/interim",
                "data/processed", "logs"):
        exists = (root / sub).is_dir()
        print(f"  [{OK if exists else MISS}] {sub}")
    if (root / ".git").is_dir():
        print(f"  [{OK}] git repository initialised")
    else:
        print(f"  [{WARN}] not a git repo yet — run:  git init && git add -A && git commit -m 'initial'")
    raw = sorted((root / "data" / "raw").glob("cdv_*.gb")) if (root / "data" / "raw").is_dir() else []
    print(f"  [{OK if raw else WARN}] GenBank downloads: "
          + (", ".join(p.name for p in raw) if raw else "none yet (that's expected at first)"))
    return root


def main() -> int:
    print("=" * 66)
    print("  CDV phylodynamics — environment check")
    print(f"  {platform.system()} {platform.release()} / {platform.machine()}")
    print("=" * 66 + "\n")

    missing_py, optional_py = check_python_packages()
    missing_bin = check_binaries()
    java = check_java()
    if java:
        print(f"\n  java: {java}")
    check_repo()

    print("\n" + "=" * 66)
    if not missing_py and not missing_bin:
        print("  Everything needed is present.")
        print("  Next: open notebooks/01_explore_dataset.ipynb and run the fetch step.")
        return 0

    print("  Action needed\n")
    if missing_py:
        print(f"    conda install -y {' '.join(missing_py)}")
        print(f"    # or:  pip install {' '.join(missing_py)}\n")
    bioconda = [t for t in missing_bin if t in ("mafft", "iqtree2", "iqtree", "trimal", "seqkit", "hyphy")]
    if bioconda:
        bioconda = ["iqtree" if t == "iqtree2" else t for t in bioconda]
        print(f"    conda install -y -c bioconda {' '.join(sorted(set(bioconda)))}\n")
    if "java" in missing_bin:
        print("    Java (needed for BEAST2, Tracer, TempEst):")
        print("      conda install -y -c conda-forge openjdk")
        print("      # or download from https://adoptium.net/\n")
    if "git" in missing_bin:
        print("    Git: xcode-select --install   (macOS)\n")
    if optional_py:
        print(f"    Optional: conda install -y {' '.join(optional_py)}\n")
    print("  Re-run this script after installing.")
    print("=" * 66)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
