#!/usr/bin/env bash
# Validate that a file is well-formed PLEXOS XML.
#
# Usage:
#   bash scripts/check_plexos_xml.sh <path/to/model.xml> [--root MasterDataSet] [--strict]
#
# Checks performed:
#   1. File exists and is non-empty.
#   2. `xmllint --noout` parses the file successfully.
#   3. (optional) Top-level element matches --root (default: MasterDataSet).
#   4. --strict: also requires --root to match exactly.
#
# Exits non-zero on the first failed check.

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "usage: $0 <path/to/model.xml> [--root MasterDataSet] [--strict]" >&2
    exit 2
fi

XML_PATH="$1"
shift

EXPECTED_ROOT="MasterDataSet"
STRICT=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --root)
            EXPECTED_ROOT="$2"
            shift 2
            ;;
        --strict)
            STRICT=1
            shift
            ;;
        *)
            echo "unknown arg: $1" >&2
            exit 2
            ;;
    esac
done

if [[ ! -s "$XML_PATH" ]]; then
    echo "FAIL: file missing or empty: $XML_PATH" >&2
    exit 1
fi

if ! command -v xmllint >/dev/null 2>&1; then
    echo "FAIL: xmllint not found on PATH" >&2
    exit 1
fi

if ! xmllint --noout "$XML_PATH" 2>/tmp/plexosdb_xmllint.err; then
    echo "FAIL: xmllint parse error:" >&2
    cat /tmp/plexosdb_xmllint.err >&2
    exit 1
fi

ROOT=$(xmllint --xpath 'name(/*)' "$XML_PATH" 2>/dev/null || true)
if [[ "$ROOT" != "$EXPECTED_ROOT" ]]; then
    MSG="root element is '$ROOT', expected '$EXPECTED_ROOT'"
    if [[ $STRICT -eq 1 ]]; then
        echo "FAIL: $MSG" >&2
        exit 1
    fi
    echo "WARN: $MSG" >&2
fi

echo "OK: $XML_PATH parses; root=$ROOT"
