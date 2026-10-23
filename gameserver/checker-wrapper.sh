#!/bin/sh
set -eu
cd "${CHECKER_DIR}"
# FakeBook checkers import a sibling "shared" package one level up; put the
# checkers root on PYTHONPATH so "from shared.utils import ..." resolves.
export PYTHONPATH="$(dirname "${CHECKER_DIR}"):${PYTHONPATH:-}"
exec python3 checker.py "$@"