"""paths.py - resolve asset and user-data paths for dev runs and packaged builds."""
import os
import shutil
import sys


def _resource_dir():
    """Folder that holds textures/, sounds/ (works with PyInstaller onefile)."""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS",
                       os.path.dirname(os.path.abspath(sys.executable)))
    return os.path.dirname(os.path.abspath(__file__))


def _user_dir():
    """Writable folder for settings / saves / achievements (never the install dir)."""
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or home
    elif sys.platform == "darwin":
        base = os.path.join(home, "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(home, ".local", "share")
    folder = os.path.join(base, "A Slipery Climb")
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        return _resource_dir()
    return folder


BASE_DIR = _resource_dir()
USER_DIR = _user_dir()

# Files the old versions kept next to main.py: move them to USER_DIR once.
_DATA_FILES = ("settings.json", "achievements.json", "tutorial_seen.json")


def _migrate_old_files():
    for name in _DATA_FILES:
        src = os.path.join(BASE_DIR, name)
        dst = os.path.join(USER_DIR, name)
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                shutil.copy2(src, dst)
            except Exception:
                pass
    for slot in range(1, 6):
        name = "save_slot_%d.json" % slot
        src = os.path.join(BASE_DIR, name)
        dst = os.path.join(USER_DIR, name)
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                shutil.copy2(src, dst)
            except Exception:
                pass


# Only packaged builds migrate the old files: when running from source the
# project folder may still hold development data, and copying that into
# %APPDATA% would make a "fresh" game show progress that was never earned.
if USER_DIR != BASE_DIR and getattr(sys, "frozen", False):
    _migrate_old_files()


def asset(*parts):
    return os.path.join(BASE_DIR, *parts)


def user(name):
    return os.path.join(USER_DIR, name)
