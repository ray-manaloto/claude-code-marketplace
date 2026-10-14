import importlib.util,sys
from pathlib import Path
s=importlib.util.spec_from_file_location('review_host_lock','/Users/rmanaloto/dev/github/ray-manaloto/dotfiles/python/src/dotfiles_setup/host_lock.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert m.lock_path(m.HEAVY_GATE)==Path.home()/'.local/state/dotfiles/heavy-gate.lock'
sys.exit(m.host_lock_main(['status']))
