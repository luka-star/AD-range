#!/bin/sh
# Role dispatcher for the gameserver image. First arg = role.
#   init        -> run DB migrations, create admin user, seed the game (then exit)
#   web         -> Django dev server on :8000 (scoreboard, /admin, teams.json)
#   controller  -> ctf-controller (the clock)
#   submission  -> ctf-submission (flag submission TCP server)
#   checker     -> ctf-checkermaster for one service
set -eu

ROLE="${1:-}"

# Point the default route at the range gateway so this component can reach the team networks
# (vulnboxes) and the VPN players through it. On-subnet infra traffic (e.g. Postgres) is unaffected.
if [ -n "${GATEWAY_IP:-}" ]; then
    ip route replace default via "${GATEWAY_IP}" 2>/dev/null \
        && echo "[entrypoint] default route via ${GATEWAY_IP}" \
        || echo "[entrypoint] WARNING: could not set default route via ${GATEWAY_IP} (need NET_ADMIN?)"
fi

wait_for_db() {
    echo "[entrypoint] waiting for database ${CTF_DBHOST}:${CTF_DBPORT:-5432} ..."
    for _ in $(seq 1 60); do
        if pg_isready -h "${CTF_DBHOST}" -p "${CTF_DBPORT:-5432}" -U "${CTF_DBUSER}" >/dev/null 2>&1; then
            echo "[entrypoint] database is ready"; return 0
        fi
        sleep 2
    done
    echo "[entrypoint] database did not become ready in time"; return 1
}

case "${ROLE}" in
    init)
        wait_for_db
        # ctf-gameserver ships no migration files on purpose, so generate them first (as `make dev` does).
        echo "[entrypoint] generating migrations ..."
        django-admin makemigrations --no-input templatetags registration scoring flatpages vpnstatus
        echo "[entrypoint] applying migrations ..."
        django-admin migrate --no-input
        echo "[entrypoint] ensuring admin superuser ..."
        # DJANGO_SUPERUSER_PASSWORD is read by createsuperuser --no-input
        django-admin createsuperuser --no-input \
            --username "${WEB_ADMIN_USER:-admin}" \
            --email "admin@range.local" 2>/dev/null \
            && echo "[entrypoint] created admin user" \
            || echo "[entrypoint] admin user already exists, skipping"
        echo "[entrypoint] seeding game configuration ..."
        python3 /opt/seed.py
        echo "[entrypoint] init complete."
        ;;
    web)
        wait_for_db
        exec django-admin runserver 0.0.0.0:8000
        ;;
    controller)
        wait_for_db
        exec ctf-controller
        ;;
    submission)
        wait_for_db
        exec ctf-submission
        ;;
    checker)
        wait_for_db
        # ctf-checkermaster reads every option from CTF_* env vars (ConfigArgParse).
        exec ctf-checkermaster
        ;;
    *)
        echo "Unknown role: '${ROLE}'. Use: init | web | controller | submission | checker" >&2
        exit 64
        ;;
esac
