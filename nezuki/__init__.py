import os
from pathlib import Path
with open(os.path.join(os.path.dirname(__file__), "version.py"), "r") as vf:
     __version__ = vf.read().strip()
