# AGENTS.md — notes for AI coding agents working in this repo

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
- Index of all installed skills + trigger text: `~/skills/SKILLS-REGISTRY.md`.

**Routing rule for agents:** when a task matches a skill's trigger text in the
registry, read that skill's `SKILL.md` and follow its instructions/scripts.

## ⚠️ Safety scope

Some provisioned packs (reverse-skill) contain offensive-security workflows
(pentest, malware analysis, CTF). Use them **only** on apps/systems you own or
are explicitly authorized to test — the same scope as UAMT's own disclaimer.
