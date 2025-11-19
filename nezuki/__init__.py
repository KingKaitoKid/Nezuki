import os
with open(os.path.join(os.path.dirname(__file__), "..", "version.txt"), "r") as vf:
     __version__ = vf.read().strip()
