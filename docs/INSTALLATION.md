# Installation and GitHub guide

## Upload to GitHub

1. Extract the repository ZIP. Open `essentiabot-content-universal/`.
2. Create an empty repository in your GitHub account.
3. Upload the **contents** of this folder, preserving `skills/`, `docs/`, `tests/`, and `.github/`. Enable hidden files in your file manager so `.env.example`, `.gitignore`, and CI configuration are included.
4. Confirm that `skills/essentiabot-content/SKILL.md` is visible at that exact repository path.
5. Choose a license if you want to grant public reuse rights. The conversion does not choose one on your behalf.

The GitHub **Import repository** feature imports from a remote Git URL, not a local ZIP. To publish your own copy of this package, use file upload or push a local Git repository.

To obtain the original repository:

```sh
git clone https://github.com/alegp97/essentiabot-content-universal.git
cd essentiabot-content-universal
```

For a local Git workflow, from the extracted repository folder:

```sh
git init
git add .
git commit -m "Add universal Essentiabot Content skill"
```

Then follow the remote and push instructions displayed by your own newly created GitHub repository. Review staged files before pushing; never add a populated env file.

## Install in a skill-aware agent

Copy the **whole `essentiabot-content` directory**, including `scripts/`, `references/`, and the blank `.env.example`, into the host's supported skills directory. The separate skill ZIP contains precisely this directory. Restart or refresh skill discovery as required by that host.

For a standard Codex user setup with no custom skill directory, the destination is `~/.codex/skills/essentiabot-content`. If the host is configured with a different skills directory, use that directory. The optional `agents/openai.yaml` contains Codex display metadata; other agents can ignore it.

For other assistants, use their documented local-skill import mechanism. If no mechanism exists, provide `SKILL.md` as instructions and keep reference files accessible; attach the specific reference needed for the task. Code execution still depends on the host. This repository does not assert automatic compatibility with any untested vendor.

## Optional Python environment

Windows PowerShell, from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe skills/essentiabot-content/scripts/bootstrap.py --profile youtube --install
.\.venv\Scripts\python.exe skills/essentiabot-content/scripts/run_essentiabot.py "https://example.com"
```

macOS/Linux:

```sh
python3 -m venv .venv
.venv/bin/python skills/essentiabot-content/scripts/bootstrap.py --profile youtube --install
.venv/bin/python skills/essentiabot-content/scripts/run_essentiabot.py "https://example.com"
```

Web and public social extraction do not require the YouTube profile. `--install` uses a temporary isolated target directory, not a global installation. Hosts that prohibit subprocesses or pip must use their own browsing tools. Do not run simultaneous installations into the same cache.
