# Repository readiness inventory

This document distinguishes **source provisioned**, **requirements identified**,
and **runtime verified**. The table covers every source configured in
`tools/install-skills.sh`. Findings are based on the checked-out READMEs; they
are not an endorsement of third-party code, nor proof of working software.
Upstream branches and requirements can change. A `SKILL.md` is agent-readable
instructions, not a running service or an automatic Arena tool registration.

The provisioning run cloned all 38 sources and indexed 948 `SKILL.md` files.
A separate run compared their contents with fresh upstream checkouts and found
38 matches. Both runs used temporary `~/skills` copies; those can disappear
between turns. The content audit does not validate signatures, safety,
submodules, dependencies, or execution. See `SKILLS_AND_REA.md` for repeatable
provisioning and verification. Runtime verification below means actual launches,
not just cloned source; **none of the tools in this inventory were newly
launched or end-to-end tested as part of this investigation**.

## Environment observations

At inspection: Python 3.11.2, Node 22.22.3, npm and procps `ps` were on PATH;
Docker, Podman, Java, ffmpeg, Go, uv, Chromium, Ghidra and JADX were not found
on PATH, and `/dev/kvm` was absent. These observations can change between
sessions; a missing command on PATH does not prove it is absent everywhere.
This sandbox has restricted outbound hosts. Browser runtimes, Docker images,
model weights, external APIs and system package downloads may therefore fail.
The workspace does not automatically register arbitrary MCP servers with Arena.

## All configured sources

For every row, the current status is **source obtained and README inspected;
runtime not tested** unless otherwise stated. "Review skills" means use the
indexed instructions selectively after reviewing them, not bulk-executing them.
"Supported host" means the upstream tool requires a compatible agent/editor;
this does not establish that Arena supports it.

| Installer name | What it is | Setup/next check |
|---|---|---|
| [anthropics-skills](https://github.com/anthropics/skills) | Skill collection | Review individual `skills/` instructions; install host integrations only where supported. |
| [reverse-skill](https://github.com/zhaoxuya520/reverse-skill) | Reverse-engineering skill pack | Skills are readable after clone; workflows may require Java, Node, Python, a compatible agent and specific analysis tools. Java was not found on PATH. |
| [PixelRAG](https://github.com/StarTrail-org/PixelRAG) | Document/image retrieval and skills | Upstream documents `pip install pixelrag`, with optional extras for embedding/index/serve. Browser rendering and models have separate requirements; inspect before installing. |
| [SocratiCode](https://github.com/giancarloerra/SocratiCode) | Code-intelligence MCP/plugin and skills | README specifies Node 18.17+, an MCP-capable host, and Docker for its default local stack; Docker was not found. Default services may require model/image downloads. |
| [BlueTeam-Tools](https://github.com/A-poc/BlueTeam-Tools) | Defensive security collection | Catalog, not a single installable program; choose and assess individual tools. |
| [RedTeam-Tools](https://github.com/A-poc/RedTeam-Tools) | Security tool collection | Catalog, not a single installable program; select individual tools and use only within authorized scope. |
| [RedteamAgent](https://github.com/NeoTheCapt/RedteamAgent) | Security-agent workflows and skills | README lists Docker/Compose and a supported AI CLI for relevant modes; Docker was not found. |
| [arena-skill](https://github.com/Jakeschincariol/arena-skill) | Agent workflow skill | README says it requires Claude Code subagents and Python 3.8+; cloning does not supply that host integration. |
| [watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) | Skill and optional Python service | README says core scripts use Python 3.10+ stdlib; review ownership, functionality and scripts before use. API/model features have additional requirements. |
| [claude-skills](https://github.com/alirezarezvani/claude-skills) | Skill collection | Review indexed skills; upstream supports `npx skills add` and other host-specific installation paths. |
| [security-audit-skill](https://github.com/cloudflare/security-audit-skill) | Security review skill | Review the skill; README lists Node for its validators. Host registration is separate. |
| [best-skills](https://github.com/LinklyAI/best-skills) | Skill rankings/catalog and a skill | Review the ranking and indexed skill; the catalog does not install all listed skills. |
| [CyberScraper-2077](https://github.com/itsOwen/CyberScraper-2077) | Python web scraping application | README lists Python 3.10+ and `requirements.txt`; browser binaries, external services or keys may be needed by selected features. No live run tested here. |
| [rea](https://github.com/morluto/rea) | Reverse-engineering CLI/MCP and skills | `rea-agents` 6.9.0 declared Node `^22.23.4 || ^24.22.1 || >=26.12.1`; inspected Node 22.22.3 did not satisfy it. Native analysis needs a configured provider; MCP host support is separate. |
| [Awesome-REA](https://github.com/reacher-z/Awesome-REA) | Reverse-engineering catalog | Browse README or structured data; linked tools are not installed. |
| [flowsint](https://github.com/reconurge/flowsint) | OSINT graph application | Upstream's documented setup uses Docker and, for Linux/macOS, Make; Docker was not found. |
| [universal-modder](https://github.com/rehan-remade/universal-modder) | Modding skill collection and workflows | README lists Git, Python 3.10+ and ffmpeg; uv recommended and Blender needed for certain 3D tasks. ffmpeg and uv were not found. |
| [101-skills-superpowers](https://github.com/101-skills/superpowers) | Inference.sh-oriented skill collection | Review indexed skills; README says CLI-backed tasks require its `belt` CLI and may need service access. |
| [cloudflare-skills](https://github.com/cloudflare/skills) | Cloudflare skill collection | Review skills; upstream documents host installation using `npx skills`. Cloud actions require appropriate accounts and permissions. |
| [designed-by-ai-skills](https://github.com/designed-by-ai/skills) | Sleek design skill | README lists a Sleek account and service access; review costs and external data handling. |
| [flowkit-labs-skills](https://github.com/flowkit-labs/skills) | Website and outreach skills | Review each skill; some workflows use external services, so verify access and consent. |
| [heygen-com-hyperframes](https://github.com/heygen-com/hyperframes) | Video framework and skills | Upstream documents CLI and skill installation; rendering and browser dependencies are separate and not tested. |
| [mattpocock-skills](https://github.com/mattpocock/skills) | Agent skill collection | Review indexed skills; README documents plugin or `npx skills` setup for compatible hosts. |
| [microsoft-azure-skills](https://github.com/microsoft/azure-skills) | Azure skills and integrations | Review relevant skills; README lists Node 18+ for MCP and host-specific setup. Azure access/permissions depend on the workflow. |
| [microsoft-playwright-cli](https://github.com/microsoft/playwright-cli) | Browser automation CLI and skills | README specifies Node 20+ and CLI installation; browser binaries and runtime access must be installed and tested separately. |
| [neondatabase-agent-skills](https://github.com/neondatabase/agent-skills) | Neon database skills | Review skills; database workflows may require Neon access and a supported integration. |
| [prisma-skills](https://github.com/prisma/skills) | Prisma skill collection | Review skills; install and configure Prisma/database dependencies only for relevant projects. |
| [remotion-dev-skills](https://github.com/remotion-dev/skills) | Remotion video skills | Review skills; actual rendering needs a separately configured Remotion project and its dependencies. |
| [supabase-agent-skills](https://github.com/supabase/agent-skills) | Supabase skills and plugin integrations | Review skills; hosted workflows need an appropriate Supabase account and permissions. |
| [vercel-labs-agent-browser](https://github.com/vercel-labs/agent-browser) | Browser automation CLI and skills | README documents npm CLI installation and separate browser setup; source builds have additional Node/pnpm/Rust requirements. |
| [vercel-labs-agent-skills](https://github.com/vercel-labs/agent-skills) | Agent skill collection | Review individual indexed skills; host installation is separate. |
| [vercel-labs-skills](https://github.com/vercel-labs/skills) | Skills CLI and documentation | README specifies Node 22.20+ for CLI; `npx skills` modifies the chosen project/agent directories and should be reviewed before running. |
| [webvm](https://github.com/leaningtech/webvm) | Browser-based Linux VM | README documents npm-based local development and public browser deployment. Needs a compatible browser; source clone alone is not a running VM. |
| [lima](https://github.com/lima-vm/lima) | Linux VM manager | Follow upstream host-specific installation, obtain a VM image and verify virtualization support. `/dev/kvm` absent here; no VM tested. |
| [VirtualXP](https://github.com/lrusso/VirtualXP) | Browser-based VM project | README links a browser-hosted project; source includes an ISO. Check image rights, browser support and limitations before use; not tested. |
| [PC-Free](https://github.com/jephersonRD/PC-Free) | Browser-accessible Windows environment setup | README describes Codespaces/Docker and a Windows image download; Docker absent here. Verify account, image licensing, network and virtualization requirements. |
| [SpaceCore](https://github.com/FSpaceCore/SpaceCore) | Android virtualization SDK demo | README says the SDK itself is not open source and must be acquired separately; Android build/device requirements apply. |
| [BlackBox](https://github.com/FBlackBox/BlackBox) | Former Android virtualization project | Current upstream README says the project was deleted; the checkout does not contain a usable implementation. Do not assume it is installable. |

## Recommended next steps

1. Commit the installer, registry, audit and this report on the active branch so
   they persist; clone sources again in each fresh environment as necessary.
2. Decide which tools need to run **in Arena** versus on the user's Windows 11 PC.
   Arena does not expose a general mechanism to register local MCP services as
   tools for this conversation.
3. Set up one candidate at a time in an isolated environment, inspect its
   installer and dependencies, and record a real smoke test. Do not run all
   installation scripts blindly, install system-wide packages indiscriminately,
   or assume every repository is a standalone program.
4. Re-check upstream licenses, versions and availability at setup time. The
   `--force` provisioning option deletes the entire marked skills root; back
   up local additions first.
