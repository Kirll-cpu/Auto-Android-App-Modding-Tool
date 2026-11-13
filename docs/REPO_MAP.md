# 🗺️ REPO MAP — UAMT (Auto-Android-App-Modding-Tool)

Working memory for AI agents. Read this **before** changing code, and update it
when behaviour changes. Scope rules live in [AGENTS.md](../AGENTS.md).

---

## 1. What this repo is

A single-file, Termux-targeted **Android APK modding toolkit** (`uamt1.3.1.py`,
~1085 lines) published to PyPI as `uamt`, plus agent-skills provisioning.

| Path | Role |
|---|---|
| `uamt1.3.1.py` | The entire application (TUI, injection, build, signing) |
| `README.md` | User-facing feature list / Termux install steps |
| `catalog.md` | Changelog ("What's New") — update when shipping features |
| `AGENTS.md` | Rules for agents: skills provisioning + safety scope |
| `tools/install-skills.sh` | Clones 30+ skill packs into `~/skills` (outside the repo) |
| `tools/skills_registry.py` | Builds `~/skills/SKILLS-REGISTRY.md` index |
| `tools/dev-env.sh` | Non-Termux dev env: pip deps, JDK on PATH, PATH wrappers |
| `tools/smoke-test.py` | Offline sanity test (synthetic APK, no Android needed) |
| `docs/OPERATION_VIOOLA_SUMMARY.md` | Unrelated OSINT case notes kept in the repo |

There is **no package, no test suite, and no build step** — the script *is* the
product. `pip install uamt` ships essentially this file.

---

## 2. `uamt1.3.1.py` architecture

Everything is module-level functions; `main()` is the loop; `if __name__ ==
"__main__"` wraps it in `try: main()`.

### Boot sequence (lines ~1–100)
1. `install_dependencies()` runs at import time → pip-installs `rich`,
   `prompt_toolkit`, then `os.execv`s itself to restart. **Importing the module
   always executes this check** (a no-op when deps exist).
2. Runtime dirs: `$HOME/UAMT` (`UAMT_ROOT`), `$HOME/UAMT/tools`,
   `libfrida.so`, `debug.keystore`, `apkeditor.jar` (APKEditor 1.4.3 URL).
3. `get_device_abi()` → `getprop ro.product.cpu.abi`, falls back to
   `platform.machine()`; returns `unknown` when neither matches.
4. `get_aapt2_bin()` → `shutil.which("aapt2")` else bare `"aapt2"`.

### UI layer (rich + prompt_toolkit)
- `get_banner_text()` / `print_banner()` — random two-colour rounded panel.
- `file_selector(start_path, title)` — full-screen prompt_toolkit browser
  (Enter opens/selects, Ctrl-C returns `None`). Icons + colour by extension.
- `hybrid_menu(menu_title, options, show_warning)` — arrow-key menu, returns
  index or `None`. **Both return `None` on Ctrl-C — every caller must handle
  `None`, and `main()` currently does `choice == 5` *before* the `None` check
  in some paths (see Known issues).**
- `select_file_with_source()` — "storage then file" wrapper: `/sdcard` or
  `$HOME`.
- `run_with_progress(cmd, description)` — streams subprocess output, greps for
  Build/Error keywords; returns `True` when exit code is 0.

### Dependency/tool management
- `install_and_update_script()` — `pkg install root-repo`, then
  `openjdk-21 wget git aapt2 patchelf apksigner zip unzip frida-python`;
  resolves latest `baksmali/smali` release via GitHub API, downloads the
  fat JAR to `$PREFIX/share/java/{smali,baksmali}.jar` and writes
  `$PREFIX/bin/{smali,baksmali}` bash wrappers (`exec java -jar …`).
- `download_file(url, dest)` — urllib with a browser User-Agent.
- `download_frida_gadget()` — GitHub API for latest `frida/frida` tag
  (fallback `16.1.4`), offers arm64-v8a / armeabi-v7a / x86_64 / x86 with a
  `◄ YOUR DEVICE` marker, downloads `frida-gadget-<ver>-android-<arch>.so.xz`,
  `lzma`-decompresses to `$HOME/UAMT/libfrida-<abi>.so`, then copies the
  device-ABI one to `libfrida.so`.
- `select_architectures()` — comma-list or Enter for device ABI (+v7a on arm64).

### Strategy selection
- `get_major_library(apk)` — `aapt2 dump badging` → `application-label:`,
  sanitises to `lib<Label>.so` / `lib<label>.so` and looks for it under
  `lib/**`; else scans `major_libs` (il2cpp, unity, main, monosgen,
  flutter/app, cocos2d*, UE4, godot, react-native, gdx …). Returns basename
  or `None`.
- `determine_strategy(apk)` — menu `Auto | Patchelf (native) | Smali (dex)`;
  returns `("NATIVE", so)` or `("SMALI", None)`.

### Injection
- `force_inject_libs(apk, payload_info, archs)` — appends
  `lib/<arch>/<payload name>` (STORE, no compression) into the APK with
  `zipfile.ZipFile(apk, 'a')`, plus `extra_files` (Frida config/script).
  Picks `libfrida-<arch>.so` when the payload is the gadget.
- `inject_native(apk, target_so, payload, archs)`
  1. extract matching `lib/<arch>/<target_so>` into `$HOME/UAMT/native_work`
  2. `patchelf --add-needed <payload> <so>` (DT_NEEDED bump — no code patch)
  3. stream-copy the whole APK: drop `META-INF/*`, store `.so` and
     `resources.arsc`, deflate the rest
  4. `force_inject_libs` → `finalize_apk`.
  Warns per selected arch where the target lib is missing.
- `inject_smali(apk, payload, archs)`
  1. requires `baksmali smali aapt2 zip unzip`
  2. `launchable-activity` from badging → descriptor `Lcom/x/Y;`
  3. binary-string-scan every `classes*.dex` for that descriptor to pick the
     target dex (falls back to `classes.dex`)
  4. `baksmali d <dex> -o smali_out`
  5. inject `const-string v0,"<lib>"; invoke-static {v0},…loadLibrary` right
     after `.locals`/`.registers` inside the activity's `onCreate(Bundle)`
  6. `smali a` → `zip -u -j` the dex back into the copied APK
  7. `force_inject_libs` → `finalize_apk`.
- `finalize_apk(temp, final)` — `zipalign -p -f 4`, generate
  `debug.keystore` with keytool if missing (`android`/`android`),
  `apksigner sign`, copy to `/sdcard/UAMT/patched_<name>.apk`
  (falls back to internal copy if `/sdcard` is not writable).
- `connect_to_gadget()` — asks IP/port (default `127.0.0.1:27042`), then
  `frida -H host gadget [-l script.js]` attached to the live TUI terminal.
- `cleanup_temp()` — removes `native_work`, `smali_work`, `patched_*`,
  `temp_script.js`, `temp_config.json` from `$UAMT_ROOT`.

### Main loop
`Inject Frida Gadget · Inject Custom Library · Connect to Gadget · Download
Frida Gadget · Install and Update · Exit`.
Frida path builds a gadget config JSON (`interaction.type` = `listen` /
`script` / custom JSON, `on_load` = resume|wait), stored as
`libfrida.config.so`; pre-injected scripts are stored as `libfscr.so`.
Custom `.so` path asks for a name and injects `lib<name>.so`.
Smali failure triggers an automatic retry through native injection.

---

## 3. Known issues / gotchas (verified by reading + smoke test)

1. **Missing INTERNET permission is not implemented.** `README.md` advertises
   "Automatically adds missing INTERNET permission" and `AGENTS.md`/README
   promise `AndroidManifest.xml` patching — `grep -i "internet|uses-permission"`
   finds nothing in the code. Either implement (binary AXML edit, needs
   apktool/aapt2) or fix the docs.
2. **`install_dependencies()` *runs at import time*** (line 55), so any import
   of the module may `pip install` and `os.execv` the interpreter. It is a
   no-op when `rich`/`prompt_toolkit` exist, but it makes the file awkward to
   unit-test — import it with `importlib` (see `tools/smoke-test.py`).

   (Checked, *not* a bug: `install_dependencies` is at module level, line 32;
   line 31 is just a trailing-whitespace line after `get_device_abi`'s
   `return "unknown"`.)
3. **`main()` only exits cleanly on `choice == 5`.** `hybrid_menu` returns
   `None` on Ctrl-C, so `None` falls through `choice == 4/3/2`, then reaches
   the injection branch with no APK selected — the current code tolerates it
   only because `select_file_with_source()` returns `None` and loops, but there
   is no explicit cancel-exit path.
4. **`hybrid_menu`/`file_selector` return `None`**; several call sites
   (`conf_idx`, `onload_idx`, `determine_strategy`'s `choice`) do not handle it
   → `None` is treated as index 0 or raises.
5. **`subprocess.run` return codes are mostly ignored** (`check=True` only for
   `patchelf` and `zip -u`): `zipalign`, `apksigner`, `pkg install`, `keytool`
   failures are silent, producing unsigned APKs with a "Done!" message.
6. **`except:` bare clauses** swallow all failures (e.g. `force_inject_libs`
   extra files, keystore copy).
7. **`os.chdir` around `zip -u` (lines 904–906) is not exception-safe** — a
   failure inside `zip` leaves the process cwd inside `work_dir`, so later
   relative paths resolve in the wrong place.
8. **Version string is hardcoded three times** (`1.3.1` in banner, file name,
   `catalog.md`). Bump all on release.
9. `download_file` does not verify size/hash; a truncated gadget download
   silently produces a broken `libfrida.so`.
10. `cleanup_temp()` deletes `patched_*.apk` inside `$UAMT_ROOT` only; the
    `/sdcard/UAMT` copy survives (intended), but the function also nukes
    `temp_config.json` **before** signing finishes in some flows.

---

## 4. Environment (this sandbox / any non-Termux box)

Termux-specific `pkg` commands cannot run here. Provisioned and verified:

```bash
tools/install-skills.sh     # 110 skills / 1014 SKILL.md under ~/skills
tools/dev-env.sh            # pip deps + JDK + patchelf + frida-tools
python3 tools/smoke-test.py # offline APK-path test
```

Verified working: `rich`, `prompt_toolkit 3.0.53`, `frida 17.26.3`,
`patchelf 0.19.3`, `androguard`, `pyaxmlparser`, Temurin JDK 25 via `jdk4py`
(`java`, `keytool`), `patchelf --version`, `get_major_library()` +
`force_inject_libs()` against a synthetic APK.

**Unavailable here** (build-artifact hosts not on the network allowlist):
GitHub release assets → `zipalign`, `apksigner`, `aapt2`, `apktool`, `jadx`,
`adb`, Android SDK. Run those on Termux/Android or a machine with SDK access.

The script is Linux-only at runtime: `/sdcard` is hardcoded, `pkg` is Termux,
and `os.system('clear')` is POSIX. Do not "fix" these to cross-platform
without an owner decision — Termux support is the point.

---

## 5. Skill routing (matches to `~/skills/SKILLS-REGISTRY.md`)

| Task | Skill |
|---|---|
| APK unpack / smali / repack / Frida hook | `community/reverse-skill/skills/apk-reverse/SKILL.md` |
| Native `.so` / ELF analysis | `ida-reverse`, `ghidra-reverse`, `radare2`, `binary-ninja-reverse` |
| Android mobile workflow | `mobile-reverse` |
| Router table for everything else | `community/reverse-skill/skills/MASTER-ROUTING.md` + `routing.md` |
| Docs/README writing | official `doc-coauthoring`, `docs-generator` |
| UI/design of the TUI | official `frontend-design` |
| Skill authoring | official `skill-creator` |

Scope gate: reverse/offensive packs are **authorized-targets-only** — see
AGENTS.md §Safety scope. UAMT itself is for apps you own or may modify.
