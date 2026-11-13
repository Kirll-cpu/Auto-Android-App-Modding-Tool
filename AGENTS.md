# AGENTS.md — notes for AI coding agents working in this repo

> **Read first, every session:** [`docs/REPO_MAP.md`](docs/REPO_MAP.md) —
> architecture of `uamt1.3.1.py` (function-by-function), known bugs, and what
> is/isn't testable off-device. Update it whenever behaviour changes.

## 🚀 Bootstrap (once per environment)

```bash
tools/install-skills.sh     # 110 skills / ~1000 SKILL.md packs -> ~/skills (outside repo)
tools/dev-env.sh            # rich, prompt_toolkit, frida-tools, androguard, JDK, patchelf
python3 tools/smoke-test.py # offline check of the pure-Python APK paths
```

`tools/dev-env.sh` is for CI/dev boxes. On Termux the supported path is the
in-app **Install and Update** menu (it uses `pkg install`), not this script.

Known sandbox limits: `zipalign`, `apksigner`, `aapt2`, `apktool`, `jadx`,
`adb` come from Android SDK / GitHub release assets which are not reachable
here — full rebuild+sign flows can only run on Termux/Android or a box with
the SDK. `uamt1.3.1.py` also hardcodes `/sdcard` and `pkg`, so it is
Termux/Linux-targeted by design; don't make it cross-platform without an
owner decision.

## 🔧 Agent skills provisioning

This project is developed with AI-agent assistance. To give the agent its full
skill set (110+ SKILL.md packs: APK reversing, mobile/binary analysis, Frida
workflows, documents, design, web testing, …), run **once per environment**:

```bash
tools/install-skills.sh
```

- Skills install to `~/skills` (**outside this repo — never commit them**;
  workspace snapshots only persist the git repo itself, so re-run the script
  at the start of each new session/environment).
- `tools/install-skills.sh --force` refreshes everything from upstream.
- Index of installed skills + trigger text: `~/skills/SKILLS-REGISTRY.md`.
- The Awesome-REA reverse-engineering catalog is available at
  `~/skills/community/Awesome-REA/README.md`, with structured data in its
  `data/` directory. It is a resource catalog, not a skill pack or an
  installation of the tools it links to; its full repository index includes
  unreviewed entries. Evaluate linked material before using it.

**Routing rule for agents:** when a task matches a skill's trigger text in the
registry, read that skill's `SKILL.md` and follow its instructions/scripts.

## ⚠️ Safety scope

Some provisioned packs (reverse-skill) contain offensive-security workflows
(pentest, malware analysis, CTF). Use them **only** on apps/systems you own or
are explicitly authorized to test — the same scope as UAMT's own disclaimer.
