#!/usr/bin/env python3
"""Compare provisioned sources against fresh checkouts of configured upstreams.

This checks file content and symlink targets, not publisher identity, code safety,
dependencies, behavior, executable permissions, or nested submodules. It does not
execute or alter source files. Network access and temporary disk space required.
"""
import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

SCRIPT = Path(__file__).resolve().parent / 'install-skills.sh'


def sources():
    text = SCRIPT.read_text(encoding='utf-8')
    pairs = re.findall(r'^install_community\s+(\S+)\s+"(https://github\.com/[^"\s]+\.git)"\s*$', text, re.M)
    return [('anthropics-skills', 'https://github.com/anthropics/skills.git'), *pairs]


def tree(root, official=False):
    """Inventory regular file bytes and symlink targets without following links."""
    result = {}
    def walk(path):
        for item in sorted(path.iterdir()):
            rel = item.relative_to(root).as_posix()
            if rel == '.git' or (official and rel in {'community', 'SKILLS-REGISTRY.md', '.uamt-skills-root'}):
                continue
            if item.is_symlink():
                result[rel] = ('symlink', os.readlink(item))
            elif item.is_dir():
                walk(item)
            elif item.is_file():
                digest = hashlib.sha256()
                with item.open('rb') as f:
                    for block in iter(lambda: f.read(1024 * 1024), b''):
                        digest.update(block)
                result[rel] = ('file', digest.hexdigest())
            else:
                result[rel] = ('other', '')
    walk(root)
    return result


def compare(local, reference, official=False):
    ours, theirs = tree(local, official), tree(reference)
    missing = sorted(theirs.keys() - ours.keys())
    extra = sorted(ours.keys() - theirs.keys())
    changed = sorted(k for k in ours.keys() & theirs.keys() if ours[k] != theirs[k])
    return missing, extra, changed


def audit(name, url, root):
    official = name == 'anthropics-skills'
    local = root if official else root / 'community' / name
    if not local.is_dir() or (official and not (root / 'skills').is_dir()):
        return 'MISSING', 'local source not present'
    try:
        with tempfile.TemporaryDirectory(prefix='uamt-verify-') as tmp:
            ref = Path(tmp) / 'repo'
            run = subprocess.run(['git', 'clone', '--depth', '1', '--quiet', url, str(ref)],
                                 capture_output=True, text=True, timeout=300)
            if run.returncode:
                detail = run.stderr.strip().splitlines()
                return 'ERROR', 'upstream clone failed: ' + (detail[-1][:240] if detail else f'exit {run.returncode}')
            rev = subprocess.run(['git', '-C', str(ref), 'rev-parse', 'HEAD'],
                                 capture_output=True, text=True, check=True).stdout.strip()
            missing, extra, changed = compare(local, ref, official)
            if missing or extra or changed:
                samples = ', '.join((missing + extra + changed)[:3])
                return 'DIFFERENT', f'upstream {rev[:12]}; missing={len(missing)} extra={len(extra)} changed={len(changed)}; examples: {samples}'
            return 'MATCH', f'file content and symlinks match upstream checkout {rev[:12]}'
    except (OSError, subprocess.SubprocessError) as error:
        return 'ERROR', str(error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(os.environ.get('SKILLS_DIR', '~/skills')).expanduser())
    parser.add_argument('names', nargs='*', help='optional source names; default: all')
    args = parser.parse_args()
    configured = dict(sources())
    unknown = set(args.names) - configured.keys()
    if unknown:
        parser.error('unknown source(s): ' + ', '.join(sorted(unknown)))
    selected = args.names or list(configured)
    bad = 0
    for name in selected:
        status, detail = audit(name, configured[name], args.root)
        print(f'{status:9} {name}: {detail}', flush=True)
        bad += status != 'MATCH'
    print(f'Checked {len(selected)} source(s); {bad} not matched. Matches do not establish safety or runtime readiness.')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
