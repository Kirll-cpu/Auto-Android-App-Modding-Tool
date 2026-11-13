#!/usr/bin/env python3
"""smoke-test.py — offline sanity check for UAMT's pure-Python paths.

Runs without Android, Termux, aapt2 or adb. Builds a synthetic APK in a temp
dir and exercises the parts of uamt1.3.1.py that are platform-independent:

  * module imports (triggers install_dependencies(); no-op when deps exist)
  * get_device_abi() never returns an empty string
  * get_major_library() finds an engine .so in a synthetic APK
  * force_inject_libs() adds the payload to every requested ABI
  * finalize_apk() / inject_native() are skipped (need zipalign/apksigner) —
    a warning names the missing binaries instead of failing.

Usage:
    python3 tools/smoke-test.py            # exits 1 on failure
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UAMT = os.path.join(REPO, "uamt1.3.1.py")
ABIS = ["arm64-v8a", "armeabi-v7a", "x86_64", "x86"]

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{(' — ' + detail) if detail else ''}")
    if not ok:
        failures.append(name)


def build_fake_apk(path: str, lib: str = "libil2cpp.so") -> None:
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("AndroidManifest.xml", b"\x03\x00\x08\x00binary-ish")
        z.writestr("classes.dex", b"dex\n035\x00fake")
        z.writestr("resources.arsc", b"arsc")
        for abi in ("arm64-v8a", "armeabi-v7a"):
            z.writestr(f"lib/{abi}/{lib}", b"\x7fELF" + b"\x00" * 60)


def load_module():
    spec = importlib.util.spec_from_file_location("uamt", UAMT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def main() -> int:
    print(f"UAMT smoke test — {UAMT}")
    tmp = tempfile.mkdtemp(prefix="uamt-smoke-")
    try:
        print("\n[1] import + helpers")
        uamt = load_module()
        check("module imports", True)
        abi = uamt.get_device_abi()
        check("get_device_abi() non-empty", bool(abi), f"-> {abi}")

        print("\n[2] library detection")
        apk = os.path.join(tmp, "fake.apk")
        build_fake_apk(apk)
        found = uamt.get_major_library(apk)
        check("get_major_library() finds libil2cpp.so", found == "libil2cpp.so", f"-> {found}")

        print("\n[3] payload injection (zip append)")
        payload_src = os.path.join(tmp, "libpayload.so")
        with open(payload_src, "wb") as f:
            f.write(b"\x7fELF" + b"\x00" * 32)
        payload = {"path": payload_src, "name": "libsmoke.so", "extra_files": []}
        uamt.force_inject_libs(apk, payload, ["arm64-v8a", "armeabi-v7a"])
        with zipfile.ZipFile(apk) as z:
            names = set(z.namelist())
        for abi in ("arm64-v8a", "armeabi-v7a"):
            check(f"payload present for {abi}", f"lib/{abi}/libsmoke.so" in names)

        print("\n[4] external tooling")
        missing = [t for t in ("zipalign", "apksigner", "aapt2", "patchelf", "java")
                   if not shutil.which(t)]
        if missing:
            print(f"  WARN  not on PATH: {', '.join(missing)} "
                  "— native rebuild/sign paths untestable here (expected outside Termux)")
        else:
            print("  PASS  zipalign/apksigner/aapt2/patchelf/java all present")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print(f"FAILED: {len(failures)} check(s) — {', '.join(failures)}")
        return 1
    print("All smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
