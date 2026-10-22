#!/usr/bin/env bash
# Generate the secrets a production deployment needs and print them as .env lines.
# Usage:  ./scripts/gen-secrets.sh >> .env   (then edit CTF_ALLOWED_HOSTS)
# Run once; re-running produces new values. .env is gitignored -- keep it private.
set -euo pipefail
rand() { head -c "$1" /dev/urandom | base64 | tr -d '\n=+/'; }
cat <<EOF
# --- generated $(date -u +%FT%TZ) -- keep private, never commit ---
CTF_WEB_SECRET_KEY=$(rand 50 | head -c 50)
CTF_FLAGSECRET=$(head -c 24 /dev/urandom | base64)
WEB_ADMIN_PASSWORD=$(rand 12 | head -c 20)
EOF
