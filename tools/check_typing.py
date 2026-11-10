#!/usr/bin/env python3
"""Run the real type checker against every shipped stub and usage regressions."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    stubs = sorted((ROOT / "src" / "YoungLion").rglob("*.pyi"))
    command = [sys.executable, "-m", "mypy", "--no-incremental", "--python-version", "3.10"]
    status = subprocess.call(
        [*command, *map(str, stubs), str(ROOT / "tests" / "typing" / "public_api.py")], cwd=ROOT)
    if status:
        return status
    invalid = ROOT / "tests" / "typing" / "invalid_api.py"
    expected = {(line_no, match.group(1))
                for line_no, line in enumerate(invalid.read_text(encoding="utf-8").splitlines(), 1)
                if (match := re.search(r"# expect: ([\w-]+)", line))}
    result = subprocess.run([*command, *map(str, stubs), str(invalid)], cwd=ROOT,
                            capture_output=True, text=True)
    found = set()
    unexpected = []
    for line in result.stdout.splitlines():
        if ": error:" not in line:
            continue
        match = re.search(r"invalid_api\.py:(\d+): error: .*\[([\w-]+)\]$", line)
        if match:
            found.add((int(match.group(1)), match.group(2)))
        else:
            unexpected.append(line)
    if result.returncode != 1 or found != expected or unexpected:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        print(f"[typing] expected rejections: {sorted(expected)}; observed: {sorted(found)}")
        return 1
    print(f"[typing] OK — {len(expected)} invalid API uses rejected with the expected diagnostics.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
