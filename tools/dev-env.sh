#!/usr/bin/env bash
#
# dev-env.sh — provision a *development / reverse-engineering* environment for
# UAMT outside Termux (CI container, Linux dev box, Arena sandbox).
#
# UAMT itself targets Termux + Android. This script does NOT replace the
# in-app "Install and Update" flow (which uses `pkg install`); it only makes
# the repo's Python entrypoint importable and puts the host-side tooling
# (JDK, patchelf, frida-tools, androguard) on PATH so agents can reason about
# and smoke-test the code.
#
# Usage:
#   tools/dev-env.sh            # install + expose wrappers
#   source tools/dev-env.sh     # same, and keep PATH in the current shell
#
set -uo pipefail

c_info() { printf '\033[1;36m[env]\033[0m %s\n' "$*"; }
c_ok()   { printf '\033[1;32m[env]\033[0m %s\n' "$*"; }
c_warn() { printf '\033[1;33m[env]\033[0m %s\n' "$*" >&2; }

PIP_FLAGS="${PIP_FLAGS:--q --break-system-packages}"

# ---------------------------------------------------------------- Python deps
# rich + prompt_toolkit are UAMT's own runtime deps (see install_dependencies()
# in uamt1.3.1.py). The rest are host-side reversing/debug helpers.
PY_DEPS="${PY_DEPS:-rich prompt_toolkit frida-tools androguard pyaxmlparser jdk4py patchelf}"
c_info "pip install $PY_DEPS"
# shellcheck disable=SC2086
python3 -m pip install $PIP_FLAGS $PY_DEPS || c_warn "pip install reported errors"

# --------------------------------------------------------------- JDK on PATH
# jdk4py ships a full Temurin JRE (java, keytool, jstack, …) inside site-packages.
JAVA_HOME_DETECTED=""
if command -v java >/dev/null 2>&1; then
  JAVA_HOME_DETECTED="$(dirname "$(dirname "$(command -v java)")")"
else
  JDK_BIN="$(python3 - <<'PY'
try:
    import jdk4py, os
    print(os.path.join(os.path.dirname(jdk4py.__file__), "java-runtime"))
except Exception:
    print("")
PY
)"
  if [[ -n "$JDK_BIN" && -x "$JDK_BIN/bin/java" ]]; then
    JAVA_HOME_DETECTED="$JDK_BIN"
    c_info "jdk4py runtime found: $JDK_BIN"
  fi
fi

if [[ -n "$JAVA_HOME_DETECTED" ]]; then
  export JAVA_HOME="$JAVA_HOME_DETECTED"
  export PATH="$JAVA_HOME/bin:$PATH"
  c_ok "java: $("$JAVA_HOME/bin/java" -version 2>&1 | head -1)"
else
  c_warn "no JDK found — smali/baksmali/APKEditor/keytool will not run"
fi

# ------------------------------------------------- patchelf console entrypoint
# The `patchelf` wheel ships a binary but its python module is namespace-ish;
# make sure the console script is reachable.
command -v patchelf >/dev/null 2>&1 && c_ok "patchelf: $(patchelf --version 2>&1 | head -1)" \
  || c_warn "patchelf missing (native injection strategy needs it)"

command -v frida >/dev/null 2>&1 && c_ok "frida: $(frida --version 2>&1 | head -1)" \
  || c_warn "frida CLI missing (Connect to Gadget needs it)"

# ------------------------------------------------------------- UAMT work dirs
# uamt1.3.1.py expects $HOME/UAMT for tools, keystore and gadget downloads.
UAMT_ROOT="${UAMT_ROOT:-$HOME/UAMT}"
if [[ ! -d "$UAMT_ROOT" ]]; then
  mkdir -p "$UAMT_ROOT/tools"
  c_info "created $UAMT_ROOT (UAMT's runtime workdir, not part of the repo)"
fi

# ------------------------------------------------------------------- summary
c_info "runtime deps importable?"
python3 - <<'PY'
mods = ["rich", "prompt_toolkit", "frida", "androguard", "pyaxmlparser"]
for m in mods:
    try:
        __import__(m)
        print(f"  {m:16s} OK")
    except Exception as e:  # noqa: BLE001
        print(f"  {m:16s} FAIL ({e.__class__.__name__})")
PY

c_ok "done — 'python3 uamt1.3.1.py' is ready on this host (TUI needs a real terminal)"
