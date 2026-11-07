"""profiles.py - local player profiles (accounts) and their data folders.

Layout under ``paths.USER_DIR`` (e.g. ``%APPDATA%\\A Slipery Climb``)::

    settings.json              global settings, shared by every profile
                               (never touched by this module)
    profiles.json              {"current": "<id>", "profiles": [...]}
    profiles/
        p1/                    one folder per profile
            achievements.json
            tutorial_seen.json
            save_slot_1.json .. save_slot_5.json
        p7f3a2c/
            ...

``profiles.json`` stores the creation-ordered profile list and the id of the
active profile.  Every profile owns a folder below ``PROFILE_ROOT``.  Modules
that used to write straight into ``USER_DIR`` (achievements, the tutorial
flag, save slots) must resolve files through ``data_path(name)`` / ``dir_for()``
so each profile keeps its own progress.  ``settings.json`` stays global.

All writes use a temp file plus ``os.replace`` (same pattern as main.py's
``_atomic_write_json``), so a crash or a full disk cannot leave a truncated
JSON file behind.  Every filesystem operation is wrapped: a corrupt or locked
file degrades to defaults instead of raising, because broken profile data must
never stop the game from starting.

If writing ``profiles.json`` itself fails (e.g. the file is locked), the
in-memory change is still kept for the current session; the next ``load()``
falls back to the last successfully written file.

Call ``load()`` once during startup, before other modules resolve their data
paths.  Every public accessor also calls ``load()`` lazily as a safety net; if
that happens first, the bootstrap profile gets the default name "Player 1".

API used by main.py::

    load(default_name="Player 1") -> None
    all() -> list[dict]                  [{"id", "name", "created"}, ...]
    current_id() -> str
    current() -> dict
    set_current(pid) -> bool
    create(name) -> dict                 creates, does NOT switch
    rename(pid, name) -> bool
    remove(pid) -> bool
    dir_for(pid=None) -> str             folder, created on demand
    data_path(filename, pid=None) -> str
    stats(pid) -> dict                   {"cleared", "best_height", "saves"}
"""
import json
import os
import shutil
import time
import uuid

import paths


PROFILES_FILE = os.path.join(paths.USER_DIR, "profiles.json")
PROFILE_ROOT = os.path.join(paths.USER_DIR, "profiles")
SAVE_NAMES = tuple("save_slot_%d.json" % i for i in range(1, 6))

# Files older builds wrote directly into USER_DIR; moved into the first
# profile the first time the profile system boots.  settings.json is global
# and is deliberately absent.
LEGACY_FILES = ("achievements.json", "tutorial_seen.json") + SAVE_NAMES

DEFAULT_NAME = "Player 1"

_ID_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
_RESERVED_FOLDERS = frozenset(
    ["con", "prn", "aux", "nul"]
    + ["com%d" % i for i in range(1, 10)]
    + ["lpt%d" % i for i in range(1, 10)])

# Module state.  _profiles is creation-ordered; dicts are the same objects
# returned (as copies) by all()/current().
_loaded = False
_profiles = []
_current = ""


# ---------------------------------------------------------------------------
# small, never-raising helpers
# ---------------------------------------------------------------------------

def _atomic_write_json(path, data):
    """Write JSON via ``<path>.tmp`` + os.replace; False on any failure."""
    tmp = path + ".tmp"
    try:
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        return True
    except Exception:
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False


def _read_json(path):
    """Parsed JSON content, or None when missing / unreadable / corrupt."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return None


def _ensure_dir(folder):
    """mkdir -p that reports success instead of raising."""
    try:
        os.makedirs(folder, exist_ok=True)
        return True
    except Exception:
        return False


def _as_int(value):
    """Best-effort int for stats fields; 0 for bools / junk / NaN / inf."""
    try:
        if isinstance(value, bool):
            return 0
        if isinstance(value, str):
            value = float(value)
        return int(value)
    except Exception:
        return 0


def _clean_id(value):
    """Folder-safe form of a profile id; never contains a path separator."""
    text = str(value if value is not None else "")
    if len(text) > 64:
        text = text[:64]
    return "".join(ch if ch in _ID_CHARS else "_" for ch in text) or "unknown"


def _valid_id(pid):
    """True for ids this module is willing to load from disk or use as folder."""
    if not isinstance(pid, str) or not pid or len(pid) > 64:
        return False
    if pid.lower() in _RESERVED_FOLDERS:
        return False
    for char in pid:
        if char not in _ID_CHARS:
            return False
    return True


def _canonical(value):
    """Stable JSON text used to detect whether load() had to repair data."""
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    except Exception:
        return ""


def _profile_dir(pid=None):
    """Profile folder path (not created)."""
    if pid is None:
        pid = _current
    return os.path.join(PROFILE_ROOT, _clean_id(pid))


def _find(pid):
    """Profile dict for an id, or None."""
    if not isinstance(pid, str):
        return None
    for profile in _profiles:
        if profile.get("id") == pid:
            return profile
    return None


def _copy(profile):
    return {"id": profile["id"], "name": profile["name"],
            "created": profile["created"]}


# ---------------------------------------------------------------------------
# profiles.json validation, backup and persistence
# ---------------------------------------------------------------------------

def _sanitize(raw):
    """Validate a parsed profiles.json.

    Returns a clean ``{"current", "profiles"}`` dict, or None when the file is
    unusable (not an object, no valid profiles left, ...).  Entries that are
    not dicts, have a non-str / unsafe id, a non-str name or a non-numeric
    (bool excluded) created stamp are dropped.  An unknown current id falls
    back to the first profile.
    """
    if not isinstance(raw, dict):
        return None
    entries = raw.get("profiles")
    if not isinstance(entries, list) or not entries:
        return None

    clean = []
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        pid = entry.get("id")
        name = entry.get("name")
        created = entry.get("created")
        if not _valid_id(pid) or pid in seen:
            continue
        if not isinstance(name, str):
            continue
        if isinstance(created, bool) or not isinstance(created, (int, float)):
            continue
        seen.add(pid)
        clean.append({"id": pid,
                      "name": name.strip() or DEFAULT_NAME,
                      "created": float(created)})
    if not clean:
        return None

    current = raw.get("current")
    if not isinstance(current, str) or current not in seen:
        current = clean[0]["id"]
    return {"current": current, "profiles": clean}


def _backup_broken():
    """Keep a ``profiles.json.bak`` copy of an unreadable/corrupt file."""
    backup = PROFILES_FILE + ".bak"
    try:
        shutil.copy2(PROFILES_FILE, backup)
        return
    except Exception:
        pass
    try:
        with open(PROFILES_FILE, "rb") as src:
            payload = src.read()
        with open(backup, "wb") as dst:
            dst.write(payload)
    except Exception:
        pass


def _persist():
    """Atomically write the in-memory profile list; False on failure."""
    return _atomic_write_json(PROFILES_FILE, {
        "current": _current,
        "profiles": [_copy(profile) for profile in _profiles],
    })


def _move_legacy(folder):
    """Move pre-profile files from the USER_DIR root into a profile folder.

    Existing files in the profile folder win (never overwritten); locked files
    are copied instead of moved and the root copy is left in place.
    """
    if not _ensure_dir(folder):
        return
    for name in _legacy_names():
        src = os.path.join(paths.USER_DIR, name)
        dst = os.path.join(folder, name)
        try:
            if not os.path.isfile(src) or os.path.exists(dst):
                continue
            try:
                os.replace(src, dst)          # same volume: atomic rename
            except Exception:
                shutil.copy2(src, dst)
                try:
                    os.remove(src)
                except Exception:
                    pass
        except Exception:
            pass


def _legacy_names():
    """Known legacy files plus any other ``save_slot_*.json`` in USER_DIR."""
    names = list(LEGACY_FILES)
    try:
        for name in os.listdir(paths.USER_DIR):
            lower = name.lower()
            if (lower.startswith("save_slot_") and lower.endswith(".json")
                    and name not in names):
                names.append(name)
    except Exception:
        pass
    return names


def _default_profile(name):
    """The bootstrap profile: id "p1" with the caller's default name."""
    text = str(name if name is not None else "").strip() or DEFAULT_NAME
    return {"id": "p1", "name": text, "created": time.time()}


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------

def load(default_name="Player 1"):
    """Bootstrap the profile system from disk (idempotent).

    Missing or invalid ``profiles.json``: keep a ``.bak`` of the broken file,
    create profile ``p1`` with *default_name*, move legacy USER_DIR files into
    its folder and write a fresh ``profiles.json``.  A valid file is validated
    and repaired (invalid entries dropped, current id made valid) and written
    back only when something changed.  The current profile folder is always
    created.  Never raises.
    """
    global _loaded, _profiles, _current
    try:
        if _loaded:
            pid = _current or (_profiles[0]["id"] if _profiles else "")
            if pid:
                _ensure_dir(_profile_dir(pid))
            return

        _ensure_dir(PROFILE_ROOT)
        raw = _read_json(PROFILES_FILE)
        data = _sanitize(raw) if raw is not None else None

        if data is None:
            # Missing, unreadable or corrupt: back up and start over.
            if os.path.exists(PROFILES_FILE):
                _backup_broken()
            profile = _default_profile(default_name)
            _profiles = [profile]
            _current = profile["id"]
            _ensure_dir(_profile_dir(_current))
            _move_legacy(_profile_dir(_current))
            _persist()
        else:
            _profiles = data["profiles"]
            _current = data["current"]
            _ensure_dir(_profile_dir(_current))
            if _canonical(raw) != _canonical(data):
                _persist()      # persist repaired entries / fallback current
        _loaded = True
    except Exception:
        # Last resort: keep a usable in-memory profile even if the disk is
        # completely unusable (read-only install, disconnected drive, ...).
        if not _profiles:
            profile = _default_profile(default_name)
            _profiles = [profile]
            _current = profile["id"]
        _loaded = True


def all():
    """All profiles as ``[{"id", "name", "created"}, ...]``, creation order."""
    if not _loaded:
        load()
    return [_copy(profile) for profile in _profiles]


def current_id():
    """Id of the active profile (never empty once load() ran)."""
    if not _loaded:
        load()
    if not _current and _profiles:
        return _profiles[0]["id"]
    return _current


def current():
    """The active profile as ``{"id", "name", "created"}``."""
    global _current
    if not _loaded:
        load()
    profile = _find(_current)
    if profile is None:
        if not _profiles:
            load()
        if _profiles:
            profile = _profiles[0]
            _current = profile["id"]
    if profile is None:                      # pathological, never raise
        profile = _default_profile(DEFAULT_NAME)
    return _copy(profile)


def set_current(pid):
    """Switch the active profile and persist; False if the id is unknown."""
    global _current
    if not _loaded:
        load()
    profile = _find(pid)
    if profile is None:
        return False
    if pid != _current:
        _current = pid
        _ensure_dir(_profile_dir(pid))
        _persist()
    return True


def create(name):
    """Create a profile with a unique short id and its folder.

    Does not switch to the new profile.  Returns its dict.
    """
    if not _loaded:
        load()
    text = str(name if name is not None else "").strip() or DEFAULT_NAME
    taken = set(profile["id"] for profile in _profiles)
    pid = _new_id(taken)
    profile = {"id": pid, "name": text, "created": time.time()}
    _profiles.append(profile)
    _ensure_dir(_profile_dir(pid))
    _persist()
    return _copy(profile)


def _new_id(taken):
    """A short id not used by any profile or existing profile folder."""
    for _ in range(32):
        candidate = "p" + uuid.uuid4().hex[:6]
        if candidate in taken:
            continue
        try:
            if os.path.isdir(os.path.join(PROFILE_ROOT, candidate)):
                continue
        except Exception:
            pass
        return candidate
    while True:                              # practically unreachable
        candidate = "p" + uuid.uuid4().hex
        if candidate not in taken:
            return candidate


def rename(pid, name):
    """Rename a profile; False for unknown id or blank name."""
    if not _loaded:
        load()
    profile = _find(pid)
    if profile is None:
        return False
    text = str(name if name is not None else "").strip()
    if not text:
        return False
    if profile["name"] != text:
        profile["name"] = text
        _persist()
    return True


def remove(pid):
    """Delete a profile and its folder; refuses current / last profile."""
    if not _loaded:
        load()
    profile = _find(pid)
    if profile is None:
        return False
    if pid == _current or len(_profiles) <= 1:
        return False
    folder = _profile_dir(pid)
    try:
        shutil.rmtree(folder, ignore_errors=True)
    except Exception:
        pass
    try:
        _profiles.remove(profile)
    except ValueError:
        pass
    _persist()
    return True


def dir_for(pid=None):
    """Folder for *pid* (default: current profile), created if missing."""
    if not _loaded:
        load()
    if pid is None:
        pid = _current
    folder = _profile_dir(pid)
    _ensure_dir(folder)
    return folder


def data_path(filename, pid=None):
    """Path of *filename* inside a profile folder (default: current)."""
    name = os.path.basename(str(filename)) if filename is not None else ""
    if not name or name in (".", ".."):
        name = "data.json"
    return os.path.join(dir_for(pid), name)


def stats(pid):
    """Per-profile summary: cleared, best_height, existing save slots.

    Reads ``achievements.json`` and checks SAVE_NAMES.  Never raises; missing
    or corrupt data yields ``{"cleared": False, "best_height": 0, "saves": 0}``.
    """
    result = {"cleared": False, "best_height": 0, "saves": 0}
    try:
        if not _loaded:
            load()
        folder = _profile_dir(pid)
        data = _read_json(os.path.join(folder, "achievements.json"))
        if isinstance(data, dict):
            clears = _as_int(data.get("clears"))
            height = _as_int(data.get("max_height"))
            result["cleared"] = clears >= 1
            result["best_height"] = height if height > 0 else 0
        saves = 0
        for name in SAVE_NAMES:
            try:
                if os.path.isfile(os.path.join(folder, name)):
                    saves += 1
            except Exception:
                pass
        result["saves"] = saves
    except Exception:
        return {"cleared": False, "best_height": 0, "saves": 0}
    return result


__all__ = [
    "PROFILES_FILE", "PROFILE_ROOT", "SAVE_NAMES",
    "load", "all", "current_id", "current", "set_current", "create",
    "rename", "remove", "dir_for", "data_path", "stats",
]
