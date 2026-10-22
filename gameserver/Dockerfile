# CTF Gameserver image: one image, several roles (web / controller / submission / checker / init).
# Built from YOUR ctf-gameserver source tree (passed as the build context) so the sim runs the
# exact code you will host.
FROM python:3.13-slim

# ---- system deps -----------------------------------------------------------
#  - curl/unzip: used by `make ext` to fetch the web frontend assets (bootstrap, jquery, fontawesome)
#  - iproute2:   so the entrypoint can point the default route at the range gateway
#  - postgresql-client: handy for debugging; `pg_isready` in healthchecks
#  - build-essential + lib headers: for building Pillow / avif wheels used by the GIFaway checkers
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl unzip iproute2 postgresql-client iputils-ping \
        build-essential libjpeg-dev zlib1g-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
# Your ctf-gameserver checkout is synced into gameserver/_src by the ./range runner before building
# (so no special Compose features are needed). The build context is this bundle's gameserver/ dir,
# which contains both _src/ and the helper files COPYed further down.
COPY _src/ /src/

# Fetch the web frontend assets into the package's static/ext dir, then install the package.
# `make ext` needs network at build time (allowed) and writes into src/.../static/ext which is
# picked up as package-data by the install below.
RUN make ext || (echo "make ext failed (frontend assets) - continuing, scoreboard may look unstyled" && true)

# Install the gameserver itself (provides ctf-controller, ctf-submission, ctf-checkermaster,
# django-admin entry points) plus the runtime deps for Postgres and the GIFaway checkers.
RUN pip install --no-cache-dir . psycopg2-binary gunicorn \
    && pip install --no-cache-dir requests types-requests result pillow pillow-avif-plugin

# ---- get_flagid compatibility shim ----------------------------------------
# The GIFaway checkers call checkerlib.get_flagid(tick); this ctf-gameserver checkerlib does not
# define it, and the Checker Master has no GETFLAGID action. We bridge it using the checker-state
# API (STORE/LOAD), which the Master DOES support and which persists per (service, team) across
# ticks. set_flagid additionally records the id in state keyed by tick; get_flagid reads it back.
# This touches only the installed copy inside the image, never your source tree.
COPY apply_shim.py /opt/apply_shim.py
RUN python3 /opt/apply_shim.py

# Our sim Django settings + helper scripts.
COPY sim_settings.py /opt/sim_settings.py
COPY prod_settings.py /opt/prod_settings.py
COPY seed.py /opt/seed.py
COPY entrypoint.sh /opt/entrypoint.sh
COPY checker-wrapper.sh /opt/checker-wrapper.sh
RUN chmod +x /opt/entrypoint.sh /opt/checker-wrapper.sh

# So `DJANGO_SETTINGS_MODULE=sim_settings` resolves and `import ctf_gameserver` works everywhere.
ENV PYTHONPATH=/opt
ENV DJANGO_SETTINGS_MODULE=sim_settings
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/opt/entrypoint.sh"]
