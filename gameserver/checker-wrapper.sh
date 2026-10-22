#!/bin/sh
# The Checker Master executes this with: <ip> <team_net_no> <tick>.
# We cd into the mounted checker directory so `import dto` (and friends) resolve, then exec the
# real checker. `exec` preserves file descriptors 3 and 4, which the Master uses to talk to the
# Checker Script, and the CTF_CHECKERSCRIPT env var (which tells checkerlib it is running under the
# Master) is inherited automatically.
set -eu
cd "${CHECKER_DIR}"
exec python3 checker.py "$@"
