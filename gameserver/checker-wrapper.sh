#!/bin/sh
set -eu
cd "${CHECKER_DIR}"
exec python3 checker.py "$@"