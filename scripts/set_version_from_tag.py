import os
import re
import sys
from pathlib import Path


def main() -> int:
    # Prefer VERSION from env; fallback to first CLI arg
    raw = os.environ.get("VERSION") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if not raw:
        print("ERROR: VERSION not provided (env VERSION or argv[1])", file=sys.stderr)
        return 2

    version = raw.lstrip("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        print(f"ERROR: VERSION must be X.Y.Z, got: {raw}", file=sys.stderr)
        return 2

    p = Path("pyproject.toml")
    if not p.exists():
        print("ERROR: pyproject.toml not found", file=sys.stderr)
        return 2

    s = p.read_text()
    new = re.sub(r'(?m)^(version\s*=\s*)"[^"]+"', rf'\1"{version}"', s)
    if s == new:
        print("ERROR: Failed to update [project].version in pyproject.toml", file=sys.stderr)
        return 1

    p.write_text(new)
    print(f"pyproject.toml version set to {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

