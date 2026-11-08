"""In-game update checker for A SLIPERY CLIMB.

On start-up the game asks the public GitHub Releases API for the newest tag and
compares it with ``GAME_VERSION``. When something newer exists, the menu shows
a small "Update available" dialog with a button that opens the release page in
the player's browser (no downloads and no installation happen behind their
back).

Everything here is best-effort: no network, a rate-limited API or a bad
response only means the game starts without an update prompt. Only
``https://api.github.com`` is contacted; no personal data is sent.

Testing hooks (environment variables):
  ASCLIMB_NO_UPDATE=1          disable the checker completely
  ASCLIMB_UPDATE_CHECK=1       allow the real check even when not frozen
  ASCLIMB_FAKE_UPDATE=<json>   pretend this release payload is the latest one
  ASCLIMB_FAKE_OPEN=1          do not launch a browser
"""
import json
import os
import sys
import threading
import urllib.request

REPO = "hotpot9628/A-Slipery-Climb"
API_URL = "https://api.github.com/repos/%s/releases/latest" % REPO
TIMEOUT = 8.0

_state = {"status": "idle", "info": None, "error": ""}
_last_action = {"kind": "", "target": ""}
_lock = threading.Lock()
_check_thread = None


def _copy(data):
    with _lock:
        return dict(data)


def state():
    return _copy(_state)


def last_action():
    return _copy(_last_action)


def _note_action(kind, target):
    with _lock:
        _last_action.update({"kind": kind, "target": target})


def _set_state(**kwargs):
    with _lock:
        _state.update(kwargs)


def _env_flag(name):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def version_tuple(text):
    """'v1.6.0' -> (1, 6, 0); unparsable -> ()."""
    if not text:
        return ()
    text = str(text).strip().lstrip("vV")
    numbers = []
    for part in text.replace("-", ".").replace("_", ".").split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        if digits:
            numbers.append(int(digits))
        elif numbers:
            break
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers[:3])


def is_newer(remote, local):
    try:
        return version_tuple(remote) > version_tuple(local)
    except Exception:
        return False


def _parse_release(payload):
    if not isinstance(payload, dict):
        return None
    tag = str(payload.get("tag_name") or payload.get("name") or "")
    parsed = version_tuple(tag)
    if not parsed:
        return None
    html = str(payload.get("html_url") or
               "https://github.com/%s/releases" % REPO)
    return {"tag": tag,
            "version": ".".join(str(n) for n in parsed),
            "url": html}


def _fake_release():
    raw = os.environ.get("ASCLIMB_FAKE_UPDATE", "").strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return _parse_release(data)
    except Exception:
        pass
    return {"tag": raw, "version": ".".join(str(n)
                                            for n in version_tuple(raw)),
            "url": "https://github.com/%s/releases/tag/%s" % (REPO, raw)}


def start_check(local_version):
    """Start one background check (safe to call more than once)."""
    global _check_thread
    if os.environ.get("ASCLIMB_NO_UPDATE"):
        _set_state(status="disabled", info=None, error="")
        return
    with _lock:
        if _state["status"] in ("checking", "available", "none"):
            return
    fake = _fake_release()
    if fake is not None:
        if is_newer(fake["version"], local_version):
            _set_state(status="available", info=fake, error="")
        else:
            _set_state(status="none", info=None, error="")
        return
    if not getattr(sys, "frozen", False) and not _env_flag("ASCLIMB_UPDATE_CHECK"):
        # running from source (or in the test driver): never touch the network
        _set_state(status="disabled", info=None, error="")
        return
    _set_state(status="checking", info=None, error="")
    _check_thread = threading.Thread(target=_check_worker,
                                     args=(local_version,), daemon=True)
    _check_thread.start()


def _check_worker(local_version):
    try:
        request = urllib.request.Request(
            API_URL,
            headers={"User-Agent": "A-Slipery-Climb/%s" % local_version,
                     "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8", "replace"))
        info = _parse_release(payload)
        if info is None:
            raise ValueError("unexpected release data")
        if is_newer(info["version"], local_version):
            _set_state(status="available", info=info, error="")
        else:
            _set_state(status="none", info=None, error="")
    except Exception as exc:
        _set_state(status="error", info=None, error=str(exc)[:160])


def poll():
    """Current checker state: status is idle/checking/available/none/error."""
    return state()


def open_url(url):
    """Open the release page in the default browser (no-op in tests)."""
    target = str(url or "")
    _note_action("url", target)
    if _env_flag("ASCLIMB_FAKE_OPEN") or not target:
        return True
    try:
        import webbrowser
        webbrowser.open(target)
        return True
    except Exception:
        return False


def reset():
    """Forget everything (used by the automated tests between scenarios)."""
    global _check_thread
    with _lock:
        _state.update({"status": "idle", "info": None, "error": ""})
        _last_action.update({"kind": "", "target": ""})
    _check_thread = None
