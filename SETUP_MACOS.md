# Setup — macOS

Written against a real Mac install, including the parts that go wrong.

---

## 1. Conda environment

```bash
git clone https://github.com/batyanight/cdv-phylodynamics.git
cd cdv-phylodynamics
conda env create -f environment.yml
conda activate cdv-phylo
python scripts/00_check_env.py
```

If solving hangs — Anaconda's base solver is slow on environments this size:

```bash
conda install -n base -c conda-forge mamba
mamba env create -f environment.yml
```

**Do not install project tools into `base`.** Anaconda's `base` holds `requests`
and `tqdm` as dependencies of conda itself, and conda refuses to let anything
replace them. The install appears to work, then fails at "Verifying transaction"
with `RemoveError: 'requests' is a dependency of conda`. It rolls back cleanly,
so nothing is damaged, but nothing is installed either. Always use a named
environment.

---

## 2. Java applications

BEAST2, Tracer, TempEst and FigTree are Java GUI/CLI tools and are **not** in
`environment.yml`. Download separately:

| Tool | Where | Used for |
|---|---|---|
| BEAST2 | https://www.beast2.org/ | the MCMC itself; includes BEAUti |
| Tracer | https://beast.community/tracer | ESS and trace inspection |
| TempEst | https://beast.community/tempest | root-to-tip regression |
| FigTree | https://github.com/rambaut/figtree/releases | viewing MCC trees |

These need a Java runtime. `java -version` should report 17 or later; if not,
`brew install --cask temurin` or the installer from adoptium.net.

On first launch macOS Gatekeeper will refuse to open them ("cannot be opened
because the developer cannot be verified"). Right-click the app → Open → Open,
once per app. Or: System Settings → Privacy & Security → "Open Anyway".

**BEAST2 on Apple Silicon.** The x86 build runs under Rosetta and is noticeably
slower. Take the aarch64 build if your Mac is M-series (`uname -m` reports
`arm64`).

---

## 3. Git

Apple's bundled git is old. Check:

```bash
git --version
```

Below 2.28 you do not have `git init -b`, and `git init -b main` fails with
`unknown switch 'b'`. Use:

```bash
git init
git checkout -b main
```

Or install a current git: `brew install git`, then restart your shell.

**Comments pasted from documentation.** zsh does not enable interactive comments
by default, so a pasted line like `rm -rf build   # the old folder` passes `#`,
`the` and `old` to `rm` as arguments. Enable them once:

```bash
echo 'setopt interactive_comments' >> ~/.zshrc
```

---

## 4. Pushing to GitHub

GitHub no longer accepts account passwords over HTTPS. You need a personal
access token: https://github.com/settings/tokens → Generate new token (classic).

Scopes needed:

- **`repo`** — always
- **`workflow`** — only if the repo contains `.github/workflows/`. Without it
  the push is rejected with *"refusing to allow a Personal Access Token to
  create or update workflow"*, after the objects have already uploaded.

Paste the token where git asks for a **password**. The prompt shows nothing as
you type — no dots, no cursor movement. That is normal.

If a stale token is cached and git stops prompting:

```bash
printf "protocol=https\nhost=github.com\n\n" | git credential-osxkeychain erase
```

Then push again. If it still does not prompt, open Keychain Access, search
`github.com`, and delete the entry.

---

## 5. Compute planning

The published analysis is two chains of 10⁸ states on the 162-sequence clade-3
alignment with a 5-state discrete trait.

- Roughly 2–4 days per chain on an M-series Mac, the two chains in parallel.
- Run them from a terminal, not BEAUti's launcher, so the process survives
  logout: `nohup beast -seed 12345 -threads 2 ... &`
- **Disable App Nap / sleep**, or macOS will throttle a long-running background
  process. `caffeinate -i beast ...` is the simplest guard.
- The 20 date-randomisation replicates are 2×10⁷ states each — a few hours
  apiece, and they can run sequentially in the background.
- Disk: the `.trees` files are the large output. Budget a few GB per chain, and
  note `.gitignore` excludes them.

### Before you start any chain

Check the tip-date direction:

```bash
grep -o 'traitname="date-[a-z]*"' your_analysis.xml
```

It must say `date-forward`. BEAUti has written `date-backward` here before, and
that error survived a full 10⁸-state run because the chain converges perfectly
well on the wrong model — no sampler diagnostic catches it. See METHODS.md §9.5
and `BEAST_MANIFEST.md`.

One second of checking against several days of compute.
