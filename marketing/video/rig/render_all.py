#!/usr/bin/env python3
"""
render_all.py — render every scene spec in a book directory, with both proofs.

For each <dir>/*.json: rig.py --verify (background pixel-identical to the plate,
every frame) then check_frame0.py (frame 0 identical to the ORIGINAL ART outside
the reconstructed hole), and a QA filmstrip. Exits non-zero if any scene fails,
so a batch is either clean or it names the scene that broke.

  python render_all.py <book-dir> [--only scene-id ...] [--dur 6.0]
"""
import argparse
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book_dir")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--no-strip", action="store_true")
    args = ap.parse_args()
    book = os.path.abspath(args.book_dir)

    specs = sorted(glob.glob(os.path.join(book, "*.json")))
    if args.only:
        specs = [s for s in specs if os.path.basename(s)[:-5] in args.only]
    if not specs:
        raise SystemExit(f"no scene json in {book}")

    failures = []
    for spec in specs:
        sid = os.path.basename(spec)[:-5]
        print(f"\n=================== {sid}")
        rc, out = run([PY, os.path.join(HERE, "rig.py"), spec, "--verify"], book)
        print(out)
        if rc != 0:
            failures.append((sid, "rig --verify"))
            continue
        clip = json.load(open(spec))["out"]
        rc, out = run([PY, os.path.join(HERE, "check_frame0.py"), spec], book)
        print(out)
        if rc != 0:
            failures.append((sid, "frame0 vs original art"))
        if not args.no_strip:
            strip = os.path.join(book, "out", f"filmstrip-{sid}.png")
            rc, out = run([PY, os.path.join(HERE, "strip.py"),
                           os.path.join(book, clip), strip], book)
            print(out)

    print(f"\n{len(specs) - len(failures)}/{len(specs)} scenes passed both proofs")
    for sid, why in failures:
        print(f"  FAILED {sid}: {why}")
    if failures:
        sys.exit(2)


if __name__ == "__main__":
    main()
