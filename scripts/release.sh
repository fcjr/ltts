#!/usr/bin/env bash
set -euo pipefail

# Interactive helper to create, push, and release a new semver tag (vX.Y.Z).
# - No arguments or flags; always interactive.
# - Shows the latest remote v* tag and suggests the next patch version.
# - Validates input is semver and greater than the latest remote v* tag.
# - Creates annotated tag, pushes it, and creates a GitHub release via gh.
# Usage:
#   scripts/release.sh

usage() { echo "Usage: $0"; }

if [[ $# -gt 0 ]]; then usage; exit 1; fi

:

# Fetch remote tags and determine latest v* tag
git fetch --tags -q
LATEST_TAG=$(git tag --list 'v*' --sort=-v:refname | head -n1)

if [[ -n ${LATEST_TAG} ]]; then
  LATEST_VER=${LATEST_TAG#v}
  # Compute suggested next patch version
  IFS='.' read -r MAJ MIN PAT <<< "${LATEST_VER}"
  SUGGESTED_VER="$MAJ.$MIN.$((PAT+1))"
  # Compare versions using sort -V
  echo "Latest remote tag: ${LATEST_TAG}" >&2
else
  echo "No existing v* tags found on remote." >&2
  SUGGESTED_VER="0.1.0"
fi

read -rp "Enter new version [${SUGGESTED_VER}]: " VERSION_INPUT
VERSION="${VERSION_INPUT:-$SUGGESTED_VER}"

# Validate semver X.Y.Z
if [[ ! ${VERSION} =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must be semver X.Y.Z (e.g., ${SUGGESTED_VER})" >&2
  exit 1
fi

# Ensure new version is greater than latest if latest exists
if [[ -n ${LATEST_TAG} ]]; then
  ORDER=$(printf "%s\n%s\n" "${LATEST_VER}" "${VERSION}" | sort -V | tail -n1)
  if [[ "${ORDER}" != "${VERSION}" || "${VERSION}" == "${LATEST_VER}" ]]; then
    echo "New version ${VERSION} must be greater than latest ${LATEST_VER}" >&2
    exit 1
  fi
fi

TAG="v${VERSION}"

echo "Creating and pushing ${TAG}..." >&2

# Double-check local non-existence
if git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null; then
  echo "Tag ${TAG} already exists locally" >&2
  exit 1
fi

# Create, push, and create GitHub release
git tag -a "${TAG}" -m "Release ${TAG}"
git push origin "${TAG}"

if command -v gh >/dev/null 2>&1; then
  gh release create "${TAG}" -t "${TAG}" -n "Release ${TAG}"
else
  echo "gh not found; skipping GitHub release creation" >&2
fi

echo "Done. Created and pushed ${TAG}." >&2
