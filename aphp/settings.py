import os

_this_folder = os.path.abspath(os.path.dirname(__file__))

REPO_ABSPATH = os.path.abspath(os.path.join(_this_folder, ".."))
SQLITE_ABSPATH = os.path.abspath(os.path.join(REPO_ABSPATH, "data", "data.db"))
