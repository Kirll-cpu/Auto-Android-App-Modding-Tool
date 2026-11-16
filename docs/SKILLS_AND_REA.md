# Skills provisioning and REA

Run `tools/install-skills.sh` to clone the configured source repositories into
`~/skills`, or set `SKILLS_DIR` to another directory. Workspace environments
may discard directories outside the repository; run the installer again when
needed. The script continues past clone failures, generates the registry where
possible, lists failures and returns a nonzero status if any clone fails.
Existing directories are skipped without verification. A failed clone is staged
in a temporary directory and is not treated as installed on a later run.

`SKILLS-REGISTRY.md` indexes all `SKILL.md` files under the root by repository,
including files lacking recognizable frontmatter (marked for manual review).
It does not install dependencies, register skills with an agent, or verify that
any program runs. Rebuild it with `python3 tools/skills_registry.py ~/skills`.
Repository contents are third-party data: review instructions and scripts before
running them. Awesome-REA is a catalog; it does not install the listed tools.

`--force` **deletes the whole skills root**, including user additions, before
re-cloning. It only accepts roots created by this installer and bearing its
`.uamt-skills-root` marker; unmarked or symlinked roots are refused. To refresh
an older unmarked installation, use a fresh `SKILLS_DIR` rather than marking or
deleting a directory without inspecting it.

## REA: what remains to use it

The `morluto/rea` clone is source material, not a configured MCP server. Check
[REA's official instructions](https://github.com/morluto/rea) and the current
`rea-agents` npm package's Node.js engine requirements before installing.
Upstream documents `npx rea-agents setup` for supported agent clients and
`npx -y rea-agents@latest analyze-javascript-application /path/to/app --json`
for JavaScript analysis. Review setup's proposed changes and only run them in a
client and environment you control. An MCP server must be explicitly supported
and connected by the host agent; cloning or installing it does not add tools to
Arena's current session. Native analysis additionally needs a supported
configured provider (such as Ghidra or IDA); Android workflows may require JADX.
Check upstream documentation for the specific workflow and dependencies.

## Checking source contents

Run `python3 tools/verify_skill_sources.py` to compare every configured local
source with a fresh shallow checkout of its configured GitHub default branch.
To check specific sources: `python3 tools/verify_skill_sources.py rea Awesome-REA`.
Use `--root PATH` for a nondefault skills directory. This needs network access
and temporary disk space, can download large repositories, and may take time.
It does not overwrite existing files. A nonzero exit indicates a missing,
different, or uncheckable source. `DIFFERENT` may mean upstream changed; it
isn't by itself evidence of tampering. The output records the compared commit.

A `MATCH` means regular file contents and symlink targets matched that checkout;
it does not verify publisher identity, signatures, executable mode, submodules,
dependencies, runtime readiness, or safety. The check uses moving default
branches, not independently pinned or signed releases. Review sources before
running code. `anthropics-skills` checks the original root layout, excluding
community sources and generated registry/marker files.
