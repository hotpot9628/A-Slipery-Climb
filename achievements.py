"""achievements.py - achievement system (levels, 9 languages, JSON save).

Same-type achievements are merged into one entry with levels:
  * Climb: 10/30/50/80/110/139/180 m (13900 = summit reached, 18000 = on the summit)
  * Total clears: 1/3/5/10/25
  * Candy master: 30/60/120 in one run
Height is converted with 100px = 1m.
"""

import json
import os

import paths

FILE = paths.user("achievements.json")
PX_PER_M = 100

HEIGHT_TIERS = [1000, 3000, 5000, 8000, 11000, 13900, 18000]
CLEAR_TIERS = [1, 3, 5, 10, 25]
CANDY_TIERS = [30, 60, 120]

L = {
    "en": {"height": "Climb", "clears": "Total Clears", "candy": "Candy Master",
           "tiers": ["Start", "Climbing", "High ground", "Above the clouds",
                     "Precarious", "Summit reached", "On the summit"],
           "not_started": "Not started",
           "height_desc": "Highest {m} m", "height_next": ", next at {n} m",
           "clears_tier": "Cleared {c} times", "clears_desc": "Total clears: {c}",
           "clears_next": ", next at {n}",
           "candy_tier": "{c} in one run", "candy_desc": "Throw {c} candies in one run",
           "candy_next": ", next at {n}"},
    "zh": {"height": "登高", "clears": "通关次数", "candy": "糖果大师",
           "tiers": ["起步", "爬升", "高处", "云上", "险要", "登上山顶", "站上山顶平台"],
           "not_started": "未开始",
           "height_desc": "最高 {m} 米", "height_next": "，下一级 {n} 米",
           "clears_tier": "已通关 {c} 次", "clears_desc": "总共通关 {c} 次",
           "clears_next": "，下一级 {n} 次",
           "candy_tier": "一局 {c} 颗", "candy_desc": "一局扔出 {c} 颗糖果",
           "candy_next": "，下一级 {n} 颗"},
    "ja": {"height": "登攀", "clears": "クリア回数", "candy": "キャンディマスター",
           "tiers": ["スタート", "登り", "高所", "雲の上", "危険", "山頂到達", "山頂の上"],
           "not_started": "未開始",
           "height_desc": "最高 {m} m", "height_next": "、次は {n} m",
           "clears_tier": "{c} 回クリア", "clears_desc": "合計 {c} 回クリア",
           "clears_next": "、次は {n} 回",
           "candy_tier": "1回で {c} 個", "candy_desc": "1回のプレイで {c} 個投げる",
           "candy_next": "、次は {n} 個"},
    "ko": {"height": "등반", "clears": "클리어 횟수", "candy": "캔디 마스터",
           "tiers": ["시작", "등반", "고지대", "구름 위", "위험", "정상 도착", "정상 위"],
           "not_started": "시작 안 함",
           "height_desc": "최고 {m} m", "height_next": ", 다음 {n} m",
           "clears_tier": "{c}회 클리어", "clears_desc": "총 {c}회 클리어",
           "clears_next": ", 다음 {n}회",
           "candy_tier": "한 판에 {c}개", "candy_desc": "한 판에 사탕 {c}개 던지기",
           "candy_next": ", 다음 {n}개"},
    "ru": {"height": "Восхождение", "clears": "Прохождения", "candy": "Мастер конфет",
           "tiers": ["Старт", "Подъём", "Высота", "Над облаками", "Опасно",
                     "Вершина достигнута", "На вершине"],
           "not_started": "Не начато",
           "height_desc": "Максимум {m} м", "height_next": ", далее {n} м",
           "clears_tier": "Пройдено {c} раз", "clears_desc": "Всего прохождений: {c}",
           "clears_next": ", далее {n}",
           "candy_tier": "{c} за раз", "candy_desc": "Бросить {c} конфет за раз",
           "candy_next": ", далее {n}"},
    "de": {"height": "Aufstieg", "clears": "Durchläufe", "candy": "Süßigkeiten-Meister",
           "tiers": ["Start", "Anstieg", "Höhe", "Über den Wolken", "Gefährlich",
                     "Gipfel erreicht", "Auf dem Gipfel"],
           "not_started": "Nicht begonnen",
           "height_desc": "Höchste {m} m", "height_next": ", nächste bei {n} m",
           "clears_tier": "{c} Mal geschafft", "clears_desc": "Insgesamt: {c}",
           "clears_next": ", nächste bei {n}",
           "candy_tier": "{c} in einem Lauf", "candy_desc": "Wirf {c} Süßigkeiten in einem Lauf",
           "candy_next": ", nächste bei {n}"},
    "fr": {"height": "Ascension", "clears": "Parties terminées", "candy": "Maître des bonbons",
           "tiers": ["Départ", "Ascension", "Hauteur", "Au-dessus des nuages", "Périlleux",
                     "Sommet atteint", "Au sommet"],
           "not_started": "Pas commencé",
           "height_desc": "Record {m} m", "height_next": ", suivante à {n} m",
           "clears_tier": "{c} fois terminé", "clears_desc": "Total : {c}",
           "clears_next": ", suivante à {n}",
           "candy_tier": "{c} en une partie", "candy_desc": "Lance {c} bonbons en une partie",
           "candy_next": ", suivante à {n}"},
    "it": {"height": "Scalata", "clears": "Completamenti", "candy": "Maestro di caramelle",
           "tiers": ["Inizio", "Salita", "Quota", "Sopra le nuvole", "Pericoloso",
                     "Vetta raggiunta", "Sulla vetta"],
           "not_started": "Non iniziato",
           "height_desc": "Record {m} m", "height_next": ", prossimo a {n} m",
           "clears_tier": "{c} volte completato", "clears_desc": "Totale: {c}",
           "clears_next": ", prossimo a {n}",
           "candy_tier": "{c} in una partita", "candy_desc": "Lancia {c} caramelle in una partita",
           "candy_next": ", prossimo a {n}"},
    "es": {"height": "Ascenso", "clears": "Partidas completadas", "candy": "Maestro de caramelos",
           "tiers": ["Inicio", "Ascenso", "Altura", "Sobre las nubes", "Peligroso",
                     "Cumbre alcanzada", "En la cumbre"],
           "not_started": "Sin empezar",
           "height_desc": "Récord {m} m", "height_next": ", siguiente en {n} m",
           "clears_tier": "{c} veces completado", "clears_desc": "Total: {c}",
           "clears_next": ", siguiente en {n}",
           "candy_tier": "{c} en una partida", "candy_desc": "Lanza {c} caramelos en una partida",
           "candy_next": ", siguiente en {n}"},
}

state = {"clears": 0, "candies": 0, "max_height": 0, "_saved": 0}
_loaded = False


def _ensure():
    global _loaded
    if _loaded:
        return
    _loaded = True
    try:
        if os.path.exists(FILE):
            with open(FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            state["clears"] = int(d.get("clears", 0))
            state["candies"] = int(d.get("candies", 0))
            state["max_height"] = int(d.get("max_height", 0))
            state["_saved"] = state["max_height"]
    except Exception:
        pass


def _save():
    try:
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump({"clears": state["clears"], "candies": state["candies"],
                       "max_height": state["max_height"]}, f)
    except Exception:
        pass


def _level(value, tiers):
    return sum(1 for t in tiers if value >= t)


def _next_tier(value, tiers):
    for t in tiers:
        if value < t:
            return t
    return None


def update_height(h):
    _ensure()
    h = int(h)
    if h <= state["max_height"]:
        return
    before = _level(state["max_height"], HEIGHT_TIERS)
    state["max_height"] = h
    after = _level(h, HEIGHT_TIERS)
    if after != before or h - state["_saved"] >= 100:
        state["_saved"] = h
        _save()


def add_clear():
    _ensure()
    state["clears"] += 1
    _save()
    return state["clears"]


def add_candy():
    _ensure()
    state["candies"] += 1
    if state["candies"] % 10 == 0:
        _save()


def reset_run():
    _ensure()
    state["candies"] = 0
    _save()


def clears():
    _ensure()
    return state["clears"]


def max_height():
    _ensure()
    return state["max_height"]


def get_list(lang="en"):
    """返回 [{name,tier_name,desc,level,max_level,unlocked}, ...]，按语言本地化。"""
    _ensure()
    t = L.get(lang) or L["en"]

    h = state["max_height"]
    hl = _level(h, HEIGHT_TIERS)
    nxt = _next_tier(h, HEIGHT_TIERS)
    tier_name = t["tiers"][hl - 1] if hl else t["not_started"]
    desc = t["height_desc"].format(m=h // PX_PER_M)
    if nxt:
        desc += t["height_next"].format(n=nxt // PX_PER_M)

    cl = state["clears"]
    cll = _level(cl, CLEAR_TIERS)
    cnxt = _next_tier(cl, CLEAR_TIERS)
    cname = t["clears_tier"].format(c=cl)
    cdesc = t["clears_desc"].format(c=cl)
    if cnxt:
        cdesc += t["clears_next"].format(n=cnxt)

    ca = state["candies"]
    cal = _level(ca, CANDY_TIERS)
    canext = _next_tier(ca, CANDY_TIERS)
    caname = t["candy_tier"].format(c=ca)
    cadesc = t["candy_desc"].format(c=ca)
    if canext:
        cadesc += t["candy_next"].format(n=canext)

    return [
        {"id": "height", "name": t["height"], "tier_name": tier_name, "desc": desc,
         "level": hl, "max_level": len(HEIGHT_TIERS), "unlocked": hl > 0},
        {"id": "clears", "name": t["clears"], "tier_name": cname, "desc": cdesc,
         "level": cll, "max_level": len(CLEAR_TIERS), "unlocked": cll > 0},
        {"id": "candy", "name": t["candy"], "tier_name": caname, "desc": cadesc,
         "level": cal, "max_level": len(CANDY_TIERS), "unlocked": cal > 0},
    ]
