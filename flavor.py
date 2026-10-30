"""
flavor.py - one-time tutorials and fall taunts for A SLIPERY CLIMB
========================================================

Standalone helper next to main.py. main.py has only 5 changes marked "# FLAVOR";
delete flavor.py plus those 5 lines to uninstall it completely.

Feature 1: one-time tutorials
    * A yellow line is hidden for good once it has been on screen for >= 0.8 s
      and then scrolls out of view;
    * The list of hidden lines lives in tutorial_seen.json (next to this file)
      so they stay hidden on the next launch;
    * F5 clears the list and brings every tutorial back (debug).

Feature 2: fall taunts
    * Tracks the highest point while airborne and taunts when you land with a
      drop of >= 280px;
    * 6 s cooldown, not triggered in fly mode.

Coordinates: GameObject text objects already hold world coordinates.
"""

import json
import os
import random

import pygame

import i18n
import paths

SEEN_FILE = paths.user("tutorial_seen.json")

# Tutorial lines stay on screen for good: the old "hide once seen"
# behaviour made newcomers miss them.
HIDE_TUTORIALS = False

NEAR_SCREEN = 140          # this much off screen still counts as seen
SEEN_TIME = 0.8            # seconds on screen to count as seen
FALL_DROP = 280            # drop height (px) that triggers a taunt
TAUNT_COOLDOWN = 6.0
TAUNT_DURATION = 3.4
RESET_KEY = pygame.K_F5

TAUNTS = [
    "That was a long way down.",
    "Gravity: 1. You: 0.",
    "You did that on purpose, right?",
    "The floor is not a checkpoint.",
    "Skilled players don't do that. Allegedly.",
    "That is the fast way down.",
    "Your candy misses you.",
    "Bold strategy.",
    "Try again. Slower this time.",
    "I would say 'almost', but that would be a lie.",
]
SECOND_TAUNTS = [
    "Take the stairs next time.",
    "The mountain is still up there.",
    "That was free advice.",
    "Do not worry, nobody saw it.",
    "You are doing great. Statistically.",
]

_NS = None
_seen = set()              # hidden tutorials (text|x|y)
_on_screen_time = {}       # accumulated on-screen time
_air_start = 0.0           # height at take-off (for fall detection)
_was_airborne = False
_last_taunt_at = -999.0
_taunt_lines = []
_taunt_timer = 0.0


# ---------------------------------------------------------------- setup
def attach(namespace):
    global _NS
    _NS = namespace
    _load_seen()
    _apply_hidden()


def _playing():
    if _NS is None:
        return False
    return getattr(_NS.get("current_state"), "name", "") == "PLAYING"


CHATTER_COLOR = (170, 220, 255)   # chatter text color: never one-time hidden


def _texts():
    if _NS is None:
        return []
    out = []
    for o in _NS.get("game", []):
        if getattr(o, "obj_type", "") != "text":
            continue
        if tuple(getattr(o, "text_color", (0, 0, 0))) == CHATTER_COLOR:
            continue          # chatter stays visible
        out.append(o)
    return out


def _key(obj):
    return f"{obj.text}|{int(obj.x)}|{int(obj.y)}"


# ---------------------------------------------------------------- persistence
def _load_seen():
    global _seen
    try:
        if os.path.exists(SEEN_FILE):
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                _seen = set(json.load(f))
    except Exception:
        _seen = set()


def _save_seen():
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(_seen), f, ensure_ascii=False)
    except Exception:
        pass


def _apply_hidden():
    if not HIDE_TUTORIALS:
        for obj in _texts():
            obj.text_visible = True
        return
    for obj in _texts():
        if _key(obj) in _seen:
            obj.text_visible = False


def reset_tutorials():
    """F5: clear the seen list so every tutorial shows again."""
    global _seen, _on_screen_time
    _seen = set()
    _on_screen_time = {}
    try:
        if os.path.exists(SEEN_FILE):
            os.remove(SEEN_FILE)
    except Exception:
        pass
    for obj in _texts():
        obj.text_visible = True


# ---------------------------------------------------------------- input
def handle_event(event):
    if event.type == pygame.KEYDOWN and event.key == RESET_KEY:
        reset_tutorials()
        return True
    return False


# ---------------------------------------------------------------- per frame
def update(dt):
    if _NS is None or not _playing():
        return
    _tick_taunt(dt)
    _update_tutorials(dt)
    _update_fall()


def _update_tutorials(dt):
    if not HIDE_TUTORIALS:
        return
    ns = _NS
    width, height = ns["WIDTH"], ns["HEIGHT"]
    cam_x, cam_y = ns["camera_x"], ns["camera_y"]
    dirty = False
    for obj in _texts():
        if not obj.text_visible:
            continue
        key = _key(obj)
        if key in _seen:
            obj.text_visible = False
            continue
        tw, th = obj.text_surface.get_size()
        sx, sy = obj.x - cam_x, obj.y - cam_y
        visible = not (sx + tw <= 0 or sx >= width or sy + th <= 0 or sy >= height)
        if visible:
            _on_screen_time[key] = _on_screen_time.get(key, 0.0) + dt
        elif _on_screen_time.get(key, 0.0) >= SEEN_TIME:
            _seen.add(key)
            obj.text_visible = False
            dirty = True
    if dirty:
        _save_seen()


def _update_fall():
    global _air_start, _was_airborne, _last_taunt_at
    ns = _NS
    feet = ns["ground_level"] - (ns["player_y"] + ns["player_height"])

    if getattr(ns.get("devfly"), "active", False):
        _was_airborne = False
        _air_start = feet
        return

    if not ns["player_is_on_ground"]:
        if not _was_airborne:
            _air_start = feet      # height at take-off is the baseline
            _was_airborne = True
        return

    if not _was_airborne:
        _air_start = feet
        return

    drop = _air_start - feet      # drop from take-off; platform rides do not count
    now = pygame.time.get_ticks() / 1000.0
    if drop >= FALL_DROP and now - _last_taunt_at >= TAUNT_COOLDOWN:
        _last_taunt_at = now
        _show_taunt()
    _was_airborne = False
    _air_start = feet


# ---------------------------------------------------------------- taunts
def _show_taunt():
    global _taunt_lines, _taunt_timer
    first_index = random.randrange(len(TAUNTS))
    line = i18n.text(TAUNTS[first_index])
    second_index = None
    second = ""
    if random.random() < 0.5:
        second_index = random.randrange(len(SECOND_TAUNTS))
        second = i18n.text(SECOND_TAUNTS[second_index])
    _taunt_lines = [line] + ([second] if second else [])
    _taunt_timer = TAUNT_DURATION
    speak = _NS.get("play_fall_taunt_voice") if _NS is not None else None
    if callable(speak):
        speak(first_index, second_index)


def _tick_taunt(dt):
    global _taunt_timer
    if _taunt_timer > 0:
        _taunt_timer = max(0.0, _taunt_timer - dt)


def draw(screen):
    if _NS is None or _taunt_timer <= 0 or not _taunt_lines:
        return
    font = _NS.get("font") or _NS.get("small_font")
    if font is None:
        return
    alpha = int(255 * min(1.0, _taunt_timer))
    x = _NS["WIDTH"] // 2
    y = 96
    for i, line in enumerate(_taunt_lines):
        f = font if i == 0 else (_NS.get("small_font") or font)
        surf = f.render(line, True, (255, 225, 140))
        surf.set_alpha(alpha)
        rect = surf.get_rect(center=(x, y))
        screen.blit(surf, rect)
        y += rect.height + 6
