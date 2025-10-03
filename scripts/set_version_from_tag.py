import os
import re
import sys
from pathlib import Path


def replace_project_version(text: str, version: str) -> str | None:
    lines = text.splitlines(keepends=True)
    in_project = False
    changed = False
    header_re = re.compile(r"^\s*\[(?P<section>[^\]]+)\]\s*$")
    version_re = re.compile(r"^(?P<prefix>\s*version\s*=\s*)\"[^\"]*\"(?P<suffix>\s*(#.*)?\n?)$")

    for i, line in enumerate(lines):
        m = header_re.match(line)
        if m:
            in_project = (m.group("section").strip() == "project")
        elif in_project:
            vm = version_re.match(line)
            if vm:
                lines[i] = f"{vm.group('prefix')}\"{version}\"{vm.group('suffix')}"
                changed = True
                break

    if not changed:
        return None
    return "".join(lines)


def main() -> int:
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
    new = replace_project_version(s, version)
    if new is None:
        print("ERROR: Failed to update [project].version in pyproject.toml", file=sys.stderr)
        return 1

    p.write_text(new)
    print(f"pyproject.toml version set to {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
