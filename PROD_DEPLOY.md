# Production deployment — gameserver

Turns the local range's gameserver into a production-served one: gunicorn behind
nginx, `prod_settings.py` instead of `sim_settings.py`, and real secrets from
`.env`. The controller, checkers, submission and database roles are unchanged —
they are already production-shaped.

## 1. Secrets

```
./scripts/gen-secrets.sh >> .env      # appends CTF_WEB_SECRET_KEY, CTF_FLAGSECRET, WEB_ADMIN_PASSWORD
```

Then edit `.env`: set `CTF_ALLOWED_HOSTS` to your server's IP / hostname (comma-separated).
`.env` is gitignored — never commit it, and the flag secret must never reach a team box.

## 2. Build + start

```
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Runs init (migrations, admin user, `collectstatic` — no auto-seed), serves the
web role with gunicorn, and puts nginx in front on port 80.

## 3. Configure the game by hand (in /admin)

Open `http://<your-server>/admin` and log in as `admin` (password = `WEB_ADMIN_PASSWORD`):

- **Game control** — competition name, start, end, tick length
- **Services** — add your two services (slugs `gifaway_checker1` / `gifaway_checker2`)
- **Teams** — create one account per real team

Scoreboard: `http://<your-server>/competition/scoreboard`

## Not covered here (next build steps)

- Per-team vulnboxes as their own VMs (so teams patch independently)
- Real WireGuard: server LAN endpoint + one config per team, gateway rules scaled to N teams
- Ops: checker logs to journald/Graylog, scoring-DB backups, scoreboard freeze
