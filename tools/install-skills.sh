#!/usr/bin/env bash
#
# install-skills.sh — provision AI "Agent Skills" (SKILL.md packs) for this project.
#

set -euo pipefail

SKILLS_DIR="${SKILLS_DIR:-$HOME/skills}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE=0
FAILED=()
CLONED=0
PRESENT=0
[[ "${1:-}" == "--force" || "${1:-}" == "-f" ]] && FORCE=1

c_info() { printf '\033[1;36m[skills]\033[0m %s\n' "$*"; }
c_ok()   { printf '\033[1;32m[skills]\033[0m %s\n' "$*"; }
c_err()  { printf '\033[1;31m[skills]\033[0m %s\n' "$*" >&2; }

command -v git >/dev/null 2>&1 || { c_err "git is required (Termux: pkg install git)"; exit 1; }

case "$SKILLS_DIR" in
  ""|"/"|"$HOME"|"$HOME/")
    c_err "Refusing SKILLS_DIR='$SKILLS_DIR' — too dangerous."
    exit 1
    ;;
esac

# Never recursively delete an arbitrary pre-existing directory, even if a
# caller passes it as SKILLS_DIR. Only directories created by this script carry
# the marker; symlinked roots are never eligible for deletion.
if [[ $FORCE -eq 1 && ( -e "$SKILLS_DIR" || -L "$SKILLS_DIR" ) ]]; then
  if [[ -L "$SKILLS_DIR" || ! -f "$SKILLS_DIR/.uamt-skills-root" ]]; then
    c_err "--force refused: skills root is a symlink or lacks .uamt-skills-root"
    exit 1
  fi
  c_info "--force: removing managed skills directory $SKILLS_DIR"
  rm -rf -- "$SKILLS_DIR"
fi
if [[ ! -e "$SKILLS_DIR" && ! -L "$SKILLS_DIR" ]]; then
  mkdir -p "$SKILLS_DIR"
  : > "$SKILLS_DIR/.uamt-skills-root"
fi

# Clone into a temporary sibling so a failed clone is never mistaken for an
# installed repository on the next run. These are sources, not installed apps.
install_official() {
  if [[ -d "$SKILLS_DIR/skills" ]]; then
    c_info "official skills directory present — skipped (not verified)"
    PRESENT=$((PRESENT + 1))
    return
  fi
  local tmp
  tmp="$(mktemp -d)"
  c_info "cloning anthropics/skills"
  if git clone --depth 1 --quiet "https://github.com/anthropics/skills.git" "$tmp/repo" && [[ -d "$tmp/repo/skills" ]]; then
    rm -rf "$tmp/repo/.git"
    mkdir -p "$SKILLS_DIR"
    cp -a "$tmp/repo/." "$SKILLS_DIR/"
    CLONED=$((CLONED + 1))
  else
    c_err "official skills clone failed or missing skills directory"
    FAILED+=("anthropics/skills")
  fi
  rm -rf "$tmp"
}

install_community() {
  local name="$1" url="$2" dest="$SKILLS_DIR/community/$1" tmp
  if [[ -d "$dest" ]]; then
    c_info "$name present — skipped (not verified)"
    PRESENT=$((PRESENT + 1))
    return
  fi
  c_info "cloning $url"
  tmp="$(mktemp -d "$SKILLS_DIR/community/.clone-$name.XXXXXX")"
  if git clone --depth 1 --quiet "$url" "$tmp/repo"; then
    rm -rf "$tmp/repo/.git"
    mv "$tmp/repo" "$dest"
    CLONED=$((CLONED + 1))
  else
    c_err "$name clone failed"
    FAILED+=("$name")
  fi
  rm -rf "$tmp"
}

install_official
mkdir -p "$SKILLS_DIR/community"
install_community reverse-skill "https://github.com/zhaoxuya520/reverse-skill.git"
install_community PixelRAG "https://github.com/StarTrail-org/PixelRAG.git"
install_community SocratiCode "https://github.com/giancarloerra/SocratiCode.git"
install_community BlueTeam-Tools "https://github.com/A-poc/BlueTeam-Tools.git"
install_community RedTeam-Tools "https://github.com/A-poc/RedTeam-Tools.git"
install_community RedteamAgent "https://github.com/NeoTheCapt/RedteamAgent.git"
install_community arena-skill "https://github.com/Jakeschincariol/arena-skill.git"
install_community watermarks-remover "https://github.com/guillaumemeyer/watermarks-remover.git"
install_community claude-skills  "https://github.com/alirezarezvani/claude-skills.git"
install_community security-audit-skill "https://github.com/cloudflare/security-audit-skill.git"
install_community best-skills    "https://github.com/LinklyAI/best-skills.git"
install_community CyberScraper-2077 "https://github.com/itsOwen/CyberScraper-2077.git"
install_community rea "https://github.com/morluto/rea.git"
# Reverse-engineering resource catalog (not an installer for the listed tools).
install_community Awesome-REA "https://github.com/reacher-z/Awesome-REA.git"
install_community flowsint "https://github.com/reconurge/flowsint.git"
install_community universal-modder "https://github.com/rehan-remade/universal-modder.git"
install_community 101-skills-superpowers "https://github.com/101-skills/superpowers.git"
install_community cloudflare-skills "https://github.com/cloudflare/skills.git"
install_community designed-by-ai-skills "https://github.com/designed-by-ai/skills.git"
install_community flowkit-labs-skills "https://github.com/flowkit-labs/skills.git"
install_community heygen-com-hyperframes "https://github.com/heygen-com/hyperframes.git"
install_community mattpocock-skills "https://github.com/mattpocock/skills.git"
install_community microsoft-azure-skills "https://github.com/microsoft/azure-skills.git"
install_community microsoft-playwright-cli "https://github.com/microsoft/playwright-cli.git"
install_community neondatabase-agent-skills "https://github.com/neondatabase/agent-skills.git"
install_community prisma-skills "https://github.com/prisma/skills.git"
install_community remotion-dev-skills "https://github.com/remotion-dev/skills.git"
install_community supabase-agent-skills "https://github.com/supabase/agent-skills.git"
install_community vercel-labs-agent-browser "https://github.com/vercel-labs/agent-browser.git"
install_community vercel-labs-agent-skills "https://github.com/vercel-labs/agent-skills.git"
install_community vercel-labs-skills "https://github.com/vercel-labs/skills.git"

install_community webvm "https://github.com/leaningtech/webvm.git"
install_community lima "https://github.com/lima-vm/lima.git"
install_community VirtualXP "https://github.com/lrusso/VirtualXP.git"
install_community PC-Free "https://github.com/jephersonRD/PC-Free.git"
install_community SpaceCore "https://github.com/FSpaceCore/SpaceCore.git"
install_community BlackBox "https://github.com/FBlackBox/BlackBox.git"
if command -v python3 >/dev/null 2>&1 && [[ -f "$SCRIPT_DIR/skills_registry.py" ]]; then
  c_info "building SKILLS-REGISTRY.md"
  python3 "$SCRIPT_DIR/skills_registry.py" "$SKILLS_DIR"
else
  c_err "python3 or skills_registry.py unavailable — registry not generated"
  FAILED+=("registry")
fi

total="$(find "$SKILLS_DIR" -name 'SKILL.md' -type f | wc -l | tr -d ' ')"
c_info "sources: $CLONED cloned, $PRESENT already present (not verified), ${#FAILED[@]} failed"
c_info "discovered $total SKILL.md files; source presence does not mean dependencies are installed"
if (( ${#FAILED[@]} )); then
  c_err "failed: ${FAILED[*]}"
  exit 1
fi
c_ok "source provisioning complete 🎉"
