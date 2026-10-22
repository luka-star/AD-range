#!/usr/bin/env python3
"""
Seed the sim database with a ready-to-play game: game control window, the two GIFaway services,
and three teams (two players + one NOP). Idempotent: safe to run more than once.
"""
import os
import datetime

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sim_settings')
django.setup()

from django.contrib.auth.models import User               # noqa: E402
from ctf_gameserver.web.scoring.models import GameControl, Service  # noqa: E402
from ctf_gameserver.web.registration.models import Team    # noqa: E402

TICK_DURATION = int(os.environ.get('SIM_TICK_DURATION', '60'))
FLAG_PREFIX = os.environ.get('SIM_FLAG_PREFIX', 'FLAG_')

now = datetime.datetime.now(datetime.timezone.utc)

# --- Game control -----------------------------------------------------------
gc = GameControl.get_instance()
gc.competition_name = 'GIFaway Local Range'
gc.services_public = now - datetime.timedelta(seconds=5)
gc.start = now - datetime.timedelta(seconds=5)   # start immediately
gc.end = now + datetime.timedelta(hours=24)
gc.tick_duration = TICK_DURATION
gc.flag_prefix = FLAG_PREFIX
gc.registration_open = False
gc.min_net_number = 1
gc.max_net_number = 99
# Keep current_tick as-is if the game was already running; otherwise leave default (-1) so the
# controller performs the first increase to tick 0.
gc.save()
print(f'[seed] GameControl: tick={TICK_DURATION}s prefix={FLAG_PREFIX} start={gc.start} end={gc.end}')

# --- Services (one per checker, matching the course template slugs) ---------
for name, slug in [('GIFaway (Store 1)', 'gifaway_checker1'),
                   ('GIFaway (Store 2)', 'gifaway_checker2')]:
    svc, created = Service.objects.get_or_create(
        slug=slug, defaults={'name': name, 'num_flagstores': 1, 'margin': 30})
    print(f'[seed] Service {slug}: {"created" if created else "exists"}')

# --- Teams ------------------------------------------------------------------
def make_team(username, net_number, nop=False, password='ctf'):
    user, _ = User.objects.get_or_create(username=username,
                                         defaults={'email': f'{username}@range.local'})
    user.set_password(password)
    user.is_active = True
    user.save()
    team, _ = Team.objects.get_or_create(
        user=user,
        defaults={'net_number': net_number, 'informal_email': f'{username}@range.local',
                  'country': 'Denmark', 'nop_team': nop})
    team.net_number = net_number
    team.nop_team = nop
    team.country = team.country or 'Denmark'
    team.informal_email = team.informal_email or f'{username}@range.local'
    team.save()
    print(f'[seed] Team {username}: net_number={net_number} nop={nop} (login {username}/{password})')

make_team('team1', 1)
make_team('team2', 2)
make_team('nop', 99, nop=True)

print('[seed] done.')
