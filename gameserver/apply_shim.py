#!/usr/bin/env python3
# Bridge two differences between the course's GIFaway checkers and this ctf-gameserver's checkerlib,
# without changing the Checker Master or your source tree. Applied at image build time to the
# installed checkerlib copy only.
#
#   1. get_flagid(tick): the checkers call it, but this checkerlib has no such function and the
#      Master has no GETFLAGID action. We store the id in checker state (STORE/LOAD, which the Master
#      supports) keyed by tick, and read it back.
#   2. tuple results: the checkers return (CheckResult, "message") from place_flag/check_service/
#      check_flag, but this checkerlib expects a bare CheckResult. We unwrap the tuple.
import pathlib

import ctf_gameserver.checkerlib.lib as m

p = pathlib.Path(m.__file__)
src = p.read_text()

SHIM = '''

# ---- sim compatibility shim (added by the GIFaway range image) -------------
import sys as _sim_sys

_sim_orig_run_check = run_check
def run_check(checker_cls):
    # Remember the current tick so set_flagid() can key state by it.
    try:
        globals()['_sim_current_tick'] = int(_sim_sys.argv[3])
    except Exception:
        globals()['_sim_current_tick'] = None

    def _sim_unwrap(r):
        # Checkers may return (CheckResult, message); this checkerlib wants a bare CheckResult.
        if isinstance(r, tuple) and len(r) >= 1:
            return r[0]
        return r

    class _SimCoerced(checker_cls):
        def place_flag(self, tick):
            return _sim_unwrap(super().place_flag(tick))
        def check_service(self):
            return _sim_unwrap(super().check_service())
        def check_flag(self, tick):
            return _sim_unwrap(super().check_flag(tick))

    return _sim_orig_run_check(_SimCoerced)

_sim_orig_set_flagid = set_flagid
def set_flagid(data, flagstore=0):
    _sim_orig_set_flagid(data, flagstore)
    t = globals().get('_sim_current_tick')
    if t is not None:
        try:
            store_state('__sim_flagid_{}_{}'.format(t, flagstore), data)
        except Exception:
            pass

def get_flagid(tick, flagstore=0):
    try:
        return load_state('__sim_flagid_{}_{}'.format(tick, flagstore))
    except Exception:
        return None
'''

if "_SimCoerced" not in src:
    # Remove any earlier (partial) shim block before re-appending, so rebuilds stay clean.
    marker = "\n\n# ---- sim compatibility shim"
    if marker in src:
        src = src[:src.index(marker)]
    p.write_text(src + SHIM)
    print("checkerlib lib.py sim shim applied (get_flagid + tuple-result coercion)")
else:
    print("checkerlib lib.py sim shim already present")

# The checkers call checkerlib.get_flagid(...) on the PACKAGE (ctf_gameserver.checkerlib), whose
# __init__ re-exports a fixed list of names that doesn't include our new get_flagid. Re-export it
# (and the shimmed run_check/set_flagid) from the package too.
init_path = p.parent / '__init__.py'
itext = init_path.read_text()
if 'sim shim re-export' not in itext:
    init_path.write_text(itext + '\nfrom .lib import get_flagid, set_flagid, run_check  # sim shim re-export\n')
    print("checkerlib __init__.py re-exports get_flagid")
else:
    print("checkerlib __init__.py already re-exports get_flagid")
