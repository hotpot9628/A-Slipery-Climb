"""achievements.py - achievement system (9 languages, JSON save).

Normal achievements have exactly five ranks:

    Iron -> Bronze -> Gold -> Platinum -> Diamond

Hidden achievements have exactly one condition (no ranks) and stay
"???" until they are unlocked.
"""

import json
import os
import time

import paths

FILE = paths.user("achievements.json")
PX_PER_M = 100

# Five tiers for every normal achievement (exactly five -> one per rank).
TIERS = {
    "height": [1000, 3000, 8000, 13900, 18000],       # px climbed
    "clears": [1, 3, 5, 10, 25],                       # finished runs
    "candy": [150, 400, 900, 1800, 3000],              # candies thrown in one run
    "air": [25, 60, 120, 250, 500],                    # candies thrown while airborne
    "sky": [30, 90, 180, 300, 420],                    # seconds airborne in one run
    "platforms": [10, 30, 60, 90, 120],                # different platforms landed on
}

NORMAL_ORDER = ["height", "clears", "candy", "air", "sky", "platforms"]
HIDDEN_ORDER = ["statue", "selfhit", "streak", "chain", "fails"]
ALL_ORDER = NORMAL_ORDER + HIDDEN_ORDER

# Hidden achievements: one condition each (no rank ladder).
HIDDEN_TIERS = {
    "statue": 60.0,        # seconds standing still
    "selfhit": 1.5,        # seconds between throw and being blasted by your own candy
    "streak": 4.0,         # seconds airborne without landing
    "chain": 30,           # chained explosions in one run
    "fails": 7,            # falls at the same spot in one run
}

# Chain explosion window (seconds between two explosions).
CHAIN_WINDOW = 1.5

# Rank colours (icon backgrounds), used by the UI.
RANK_COLORS = [(150, 150, 160), (190, 120, 60), (240, 200, 80),
               (200, 220, 235), (120, 220, 255)]

L = {
    "en": {
        "ranks": ["Iron", "Bronze", "Gold", "Platinum", "Diamond"],
        "hidden": "Hidden", "locked": "???",
        "names": {
            "fails": "Stubborn",
            "height": "Cloud Walker", "clears": "Summit Legend",
            "candy": "Candy Storm", "air": "Aerial Ace",
            "sky": "Sky Dweller", "platforms": "Trailblazer",
            "statue": "Statue", "selfhit": "Self-Hit",
            "streak": "Air Streak", "chain": "Chain Reaction",
        },
        "req": {
            "fails": "Fall at the same spot {v} times",
            "height": "Climb {v} m", "clears": "Finish the game {v} time(s)",
            "candy": "Throw {v} candies in one run",
            "air": "Throw {v} candies while airborne in one run",
            "sky": "Spend {v} s in the air in one run",
            "platforms": "Stand on {v} different platforms in one run",
            "statue": "Stand still for {v} s",
            "selfhit": "Get blasted by a candy you threw at least {v} s earlier",
            "streak": "Stay airborne for {v} s without landing",
            "chain": "Set off {v} explosions in a row (max 1.5 s apart)",
        },
        "prog": {
            "fails": "Most falls at one spot: {c}",
            "height": "Highest {c} m", "clears": "Finished {c} time(s)",
            "candy": "{c} candies in one run", "air": "{c} air throws in one run",
            "sky": "{c} s airborne", "platforms": "{c} platforms visited",
            "statue": "{c} s standing still",
            "selfhit": "Hit by your own candy after {c} s",
            "streak": "Longest air streak {c} s",
            "chain": "Longest chain {c}",
        },
        "next": "next {n}", "max": "MAX",
    },
    "zh": {
        "ranks": ["黑铁", "青铜", "黄金", "铂金", "钻石"],
        "hidden": "隐藏", "locked": "???",
        "names": {
            "fails": "屡败屡战",
            "height": "云端行者", "clears": "山顶传奇",
            "candy": "糖果风暴", "air": "空中王牌",
            "sky": "天空居民", "platforms": "踏遍群山",
            "statue": "石像", "selfhit": "自食其果",
            "streak": "空中连击", "chain": "连锁反应",
        },
        "req": {
            "fails": "在同一个地方掉下去 {v} 次",
            "height": "爬升 {v} 米", "clears": "通关 {v} 次",
            "candy": "一局扔出 {v} 颗糖",
            "air": "一局在空中扔出 {v} 颗糖",
            "sky": "一局累计滞空 {v} 秒",
            "platforms": "一局站上 {v} 个不同平台",
            "statue": "原地不动 {v} 秒",
            "selfhit": "被自己扔出至少 {v} 秒前的糖果炸到",
            "streak": "一次滞空 {v} 秒不落地",
            "chain": "连续引爆 {v} 次，每次间隔不超过 1.5 秒",
        },
        "prog": {
            "fails": "同一处最多掉了 {c} 次",
            "height": "最高 {c} 米", "clears": "已通关 {c} 次",
            "candy": "一局 {c} 颗", "air": "一局空中 {c} 颗",
            "sky": "滞空 {c} 秒", "platforms": "已站上 {c} 个平台",
            "statue": "静止 {c} 秒",
            "selfhit": "被自己 {c} 秒前的糖果炸到",
            "streak": "最长滞空 {c} 秒",
            "chain": "最长连击 {c} 次",
        },
        "next": "下一级 {n}", "max": "已满级",
    },
    "ja": {
        "ranks": ["アイアン", "ブロンズ", "ゴールド", "プラチナ", "ダイヤモンド"],
        "hidden": "隠し", "locked": "???",
        "names": {
            "fails": "七転び八起き",
            "height": "雲の歩者", "clears": "山頂の伝説",
            "candy": "キャンディ・ストーム", "air": "空中のエース",
            "sky": "空の住人", "platforms": "山道の先駆者",
            "statue": "石像", "selfhit": "自業自得",
            "streak": "エア・ストリーク", "chain": "連鎖反応",
        },
        "req": {
            "fails": "同じ場所で {v} 回落ちる",
            "height": "{v} m 登る", "clears": "{v} 回クリアする",
            "candy": "1回のプレイで {v} 個投げる",
            "air": "空中で {v} 個投げる",
            "sky": "1回で合計 {v} 秒空中にいる",
            "platforms": "1回のプレイで {v} 個の違う足場に乗る",
            "statue": "{v} 秒間じっとしている",
            "selfhit": "{v} 秒以上前に投げたキャンディに吹き飛ばされる",
            "streak": "{v} 秒間着地せずに空中にいる",
            "chain": "1.5 秒以内に {v} 回連続で爆発させる",
        },
        "prog": {
            "fails": "同じ場所で最大 {c} 回",
            "height": "最高 {c} m", "clears": "{c} 回クリア",
            "candy": "1回で {c} 個", "air": "空中で {c} 個",
            "sky": "{c} 秒空中", "platforms": "{c} 個の足場",
            "statue": "{c} 秒静止",
            "selfhit": "{c} 秒前のキャンディに吹き飛ばされた",
            "streak": "最長 {c} 秒",
            "chain": "最長連鎖 {c} 回",
        },
        "next": "次は {n}", "max": "最大",
    },
    "ko": {
        "ranks": ["아이언", "브론즈", "골드", "플래티넘", "다이아몬드"],
        "hidden": "숨김", "locked": "???",
        "names": {
            "fails": "칠전팔기",
            "height": "구름 걷는 자", "clears": "정상의 전설",
            "candy": "캔디 스톰", "air": "에어리얼 에이스",
            "sky": "하늘 거주자", "platforms": "길잡이",
            "statue": "석상", "selfhit": "자업자득",
            "streak": "에어 스트리크", "chain": "연쇄 반응",
        },
        "req": {
            "fails": "같은 장소에서 {v}번 떨어지기",
            "height": "{v} m 오르기", "clears": "{v}회 클리어하기",
            "candy": "한 판에 사탕 {v}개 던지기",
            "air": "공중에서 {v}개 던지기",
            "sky": "한 판에 총 {v}초 공중에 있기",
            "platforms": "한 판에 {v}개의 다른 발판에 서기",
            "statue": "{v}초 동안 가만히 있기",
            "selfhit": "{v}초 전에 던진 사탕에 맞아 날아가기",
            "streak": "착지 없이 {v}초 공중에 있기",
            "chain": "1.5초 간격으로 {v}회 연속 폭발시키기",
        },
        "prog": {
            "fails": "한 장소 최다 {c}회",
            "height": "최고 {c} m", "clears": "{c}회 클리어",
            "candy": "한 판 {c}개", "air": "공중 {c}개",
            "sky": "{c}초 공중", "platforms": "{c}개 발판",
            "statue": "{c}초 정지",
            "selfhit": "{c}초 전 사탕에 맞음",
            "streak": "최장 {c}초",
            "chain": "최장 연쇄 {c}회",
        },
        "next": "다음 {n}", "max": "최대",
    },
    "ru": {
        "ranks": ["Железо", "Бронза", "Золото", "Платина", "Алмаз"],
        "hidden": "Скрытые", "locked": "???",
        "names": {
            "fails": "Упрямец",
            "height": "Идущий по облакам", "clears": "Легенда вершины",
            "candy": "Конфетный шторм", "air": "Воздушный ас",
            "sky": "Небесный житель", "platforms": "Первопроходец",
            "statue": "Статуя", "selfhit": "Сам себе враг",
            "streak": "Воздушная серия", "chain": "Цепная реакция",
        },
        "req": {
            "fails": "Упасть в одном месте {v} раз",
            "height": "Подняться на {v} м", "clears": "Пройти игру {v} раз",
            "candy": "Бросить {v} конфет за забег",
            "air": "Бросить {v} конфет в воздухе за забег",
            "sky": "Провести {v} с в воздухе за забег",
            "platforms": "Постоять на {v} разных платформах за забег",
            "statue": "Стоять неподвижно {v} с",
            "selfhit": "Получить удар от конфеты, брошенной {v} с назад",
            "streak": "Продержаться в воздухе {v} с",
            "chain": "Устроить {v} взрывов подряд (не более 1.5 с между ними)",
        },
        "prog": {
            "fails": "Больше всего падений: {c}",
            "height": "Максимум {c} м", "clears": "Пройдено {c} раз",
            "candy": "{c} конфет за забег", "air": "{c} в воздухе",
            "sky": "{c} с в воздухе", "platforms": "{c} платформ",
            "statue": "{c} с неподвижно",
            "selfhit": "Удар от конфеты {c} с назад",
            "streak": "Серия {c} с",
            "chain": "Лучшая серия {c}",
        },
        "next": "далее {n}", "max": "МАКС",
    },
    "de": {
        "ranks": ["Eisen", "Bronze", "Gold", "Platin", "Diamant"],
        "hidden": "Versteckt", "locked": "???",
        "names": {
            "fails": "Sturkopf",
            "height": "Wolkenwandler", "clears": "Gipfel-Legende",
            "candy": "Süßigkeiten-Sturm", "air": "Luft-Ass",
            "sky": "Himmelsbewohner", "platforms": "Wegbereiter",
            "statue": "Standbild", "selfhit": "Eigentor",
            "streak": "Luftserie", "chain": "Kettenreaktion",
        },
        "req": {
            "fails": "An derselben Stelle {v}-mal fallen",
            "height": "{v} m klettern", "clears": "Spiel {v}-mal beenden",
            "candy": "Wirf {v} Süßigkeiten in einem Lauf",
            "air": "Wirf {v} Süßigkeiten in der Luft",
            "sky": "Sei {v} s in einem Lauf in der Luft",
            "platforms": "Steh auf {v} verschiedenen Plattformen",
            "statue": "Steh {v} s still",
            "selfhit": "Werde von einer Süßigkeit getroffen, die du vor {v} s geworfen hast",
            "streak": "Bleib {v} s ohne Landung in der Luft",
            "chain": "Löse {v} Explosionen in Folge aus (max. 1,5 s Abstand)",
        },
        "prog": {
            "fails": "Meiste Stürze an einer Stelle: {c}",
            "height": "Höchste {c} m", "clears": "{c}-mal beendet",
            "candy": "{c} in einem Lauf", "air": "{c} in der Luft",
            "sky": "{c} s in der Luft", "platforms": "{c} Plattformen",
            "statue": "{c} s still",
            "selfhit": "Treffer nach {c} s",
            "streak": "Serie {c} s",
            "chain": "Längste Kette {c}",
        },
        "next": "nächste {n}", "max": "MAX",
    },
    "fr": {
        "ranks": ["Fer", "Bronze", "Or", "Platine", "Diamant"],
        "hidden": "Cachés", "locked": "???",
        "names": {
            "fails": "Têtu",
            "height": "Marcheur des nuages", "clears": "Légende du sommet",
            "candy": "Tempête de bonbons", "air": "As des airs",
            "sky": "Habitant du ciel", "platforms": "Pionnier",
            "statue": "Statue", "selfhit": "Autogoal",
            "streak": "Série aérienne", "chain": "Réaction en chaîne",
        },
        "req": {
            "fails": "Tomber {v} fois au même endroit",
            "height": "Monter {v} m", "clears": "Terminer le jeu {v} fois",
            "candy": "Lance {v} bonbons en une partie",
            "air": "Lance {v} bonbons en vol",
            "sky": "Reste {v} s en l'air en une partie",
            "platforms": "Tiens-toi sur {v} plateformes différentes",
            "statue": "Reste immobile {v} s",
            "selfhit": "Sois touché par un bonbon lancé il y a au moins {v} s",
            "streak": "Reste {v} s en l'air sans atterrir",
            "chain": "Provoque {v} explosions d'affilée (1,5 s max entre elles)",
        },
        "prog": {
            "fails": "Chutes au même endroit : {c}",
            "height": "Record {c} m", "clears": "{c} fois terminé",
            "candy": "{c} en une partie", "air": "{c} en vol",
            "sky": "{c} s en l'air", "platforms": "{c} plateformes",
            "statue": "{c} s immobile",
            "selfhit": "Touché par un bonbon après {c} s",
            "streak": "Série {c} s",
            "chain": "Meilleure chaîne {c}",
        },
        "next": "suivante {n}", "max": "MAX",
    },
    "it": {
        "ranks": ["Ferro", "Bronzo", "Oro", "Platino", "Diamante"],
        "hidden": "Nascosti", "locked": "???",
        "names": {
            "fails": "Testardo",
            "height": "Camminatore di nuvole", "clears": "Leggenda della vetta",
            "candy": "Tempesta di caramelle", "air": "Asso dell'aria",
            "sky": "Abitante del cielo", "platforms": "Pioniere",
            "statue": "Statua", "selfhit": "Autogol",
            "streak": "Serie aerea", "chain": "Reazione a catena",
        },
        "req": {
            "fails": "Cadere {v} volte nello stesso punto",
            "height": "Scala {v} m", "clears": "Completa il gioco {v} volte",
            "candy": "Lancia {v} caramelle in una partita",
            "air": "Lancia {v} caramelle in aria",
            "sky": "Resta {v} s in aria in una partita",
            "platforms": "Stai su {v} piattaforme diverse in una partita",
            "statue": "Resta fermo {v} s",
            "selfhit": "Fatti colpire da una caramella lanciata {v} s prima",
            "streak": "Resta {v} s in aria senza atterrare",
            "chain": "Provoca {v} esplosioni di fila (max 1,5 s di distanza)",
        },
        "prog": {
            "fails": "Cadute nello stesso punto: {c}",
            "height": "Record {c} m", "clears": "{c} volte completato",
            "candy": "{c} in una partita", "air": "{c} in aria",
            "sky": "{c} s in aria", "platforms": "{c} piattaforme",
            "statue": "{c} s fermo",
            "selfhit": "Colpito dopo {c} s",
            "streak": "Serie {c} s",
            "chain": "Catena migliore {c}",
        },
        "next": "prossima {n}", "max": "MAX",
    },
    "es": {
        "ranks": ["Hierro", "Bronce", "Oro", "Platino", "Diamante"],
        "hidden": "Ocultos", "locked": "???",
        "names": {
            "fails": "Terco",
            "height": "Caminante de nubes", "clears": "Leyenda de la cumbre",
            "candy": "Tormenta de caramelos", "air": "As del aire",
            "sky": "Habitante del cielo", "platforms": "Pionero",
            "statue": "Estatua", "selfhit": "Autogol",
            "streak": "Racha aérea", "chain": "Reacción en cadena",
        },
        "req": {
            "fails": "Caer {v} veces en el mismo sitio",
            "height": "Sube {v} m", "clears": "Termina el juego {v} veces",
            "candy": "Lanza {v} caramelos en una partida",
            "air": "Lanza {v} caramelos en el aire",
            "sky": "Pasa {v} s en el aire en una partida",
            "platforms": "Ponte en {v} plataformas distintas en una partida",
            "statue": "Quédate quieto {v} s",
            "selfhit": "Recibe el golpe de un caramelo lanzado hace {v} s",
            "streak": "Permanece {v} s en el aire sin aterrizar",
            "chain": "Provoca {v} explosiones seguidas (máx. 1,5 s entre ellas)",
        },
        "prog": {
            "fails": "Caídas en el mismo sitio: {c}",
            "height": "Récord {c} m", "clears": "{c} veces terminado",
            "candy": "{c} en una partida", "air": "{c} en el aire",
            "sky": "{c} s en el aire", "platforms": "{c} plataformas",
            "statue": "{c} s quieto",
            "selfhit": "Golpeado tras {c} s",
            "streak": "Racha {c} s",
            "chain": "Mejor cadena {c}",
        },
        "next": "siguiente {n}", "max": "MAX",
    },
}

# per-run counters; max_height / clears are lifetime
state = {
    "clears": 0, "max_height": 0,
    "candies": 0, "air_throws": 0, "chains": 0, "air_time": 0.0,
    "idle": 0.0, "selfhit": 0.0, "streak": 0.0, "platforms": 0,
    "fails": 0,
    "unlocked": {},     # hidden kind -> best value, survives restarts
    "best": {},         # normal kind -> best value ever, survives runs/restarts
    "_saved": 0,
}
NOTIFY = []
_loaded = False
_last_explosion_time = 0.0
_chain_combo = 0


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
            state["max_height"] = int(d.get("max_height", 0))
            unlocked = d.get("unlocked", {})
            if isinstance(unlocked, dict):
                state["unlocked"] = {str(k): float(v) for k, v in unlocked.items()}
            best = d.get("best", {})
            if isinstance(best, dict):
                state["best"] = {str(k): float(v) for k, v in best.items()}
            state["_saved"] = state["max_height"]
    except Exception:
        pass


def _save():
    data = {"clears": state["clears"], "max_height": state["max_height"],
            "unlocked": state["unlocked"], "best": state["best"]}
    tmp = FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, FILE)
    except Exception:
        pass


def _level(value, tiers):
    return sum(1 for t in tiers if value >= t)


def _next_tier(value, tiers):
    for t in tiers:
        if value < t:
            return t
    return None


def _notify(kind, tiers, before, after):
    for i in range(before + 1, after + 1):
        NOTIFY.append({"kind": kind, "tier": tiers[i - 1]})


def _notify_hidden(kind, before, after):
    """Hidden achievements have a single threshold and stay unlocked."""
    if kind in state["unlocked"]:
        return
    threshold = HIDDEN_TIERS[kind]
    if before < threshold <= after:
        state["unlocked"][kind] = max(after, state["unlocked"].get(kind, 0.0))
        NOTIFY.append({"kind": kind, "tier": threshold, "hidden": True})
        _save()


def _bump(key, kind):
    state[key] = state[key] + 1
    old_best = state["best"].get(kind, 0.0)
    new_best = max(old_best, state[key])
    state["best"][kind] = new_best
    before = _level(old_best, TIERS[kind])
    after = _level(new_best, TIERS[kind])
    _notify(kind, TIERS[kind], before, after)
    if after != before:
        _save()


# ---------------------------------------------------------------- lifetime
def update_height(h):
    _ensure()
    h = int(h)
    if h <= state["max_height"]:
        return
    before = _level(state["max_height"], TIERS["height"])
    state["max_height"] = h
    after = _level(h, TIERS["height"])
    _notify("height", TIERS["height"], before, after)
    if after != before or h - state["_saved"] >= 100:
        state["_saved"] = h
        _save()


def add_clear():
    _ensure()
    before = _level(state["clears"], TIERS["clears"])
    state["clears"] += 1
    after = _level(state["clears"], TIERS["clears"])
    _notify("clears", TIERS["clears"], before, after)
    _save()
    return state["clears"]


# ---------------------------------------------------------------- per run
def add_candy():
    _ensure()
    _bump("candies", "candy")


def add_air_throw():
    _ensure()
    _bump("air_throws", "air")


def add_chain():
    """Explosions closer together than CHAIN_WINDOW build a combo; a gap
    longer than that breaks it and the combo starts again from 1."""
    global _last_explosion_time, _chain_combo
    _ensure()
    now = time.time()
    if 0 < now - _last_explosion_time <= CHAIN_WINDOW:
        _chain_combo += 1
    else:
        _chain_combo = 1
    _last_explosion_time = now
    if _chain_combo > state["chains"]:
        before = state["chains"]
        state["chains"] = _chain_combo
        _notify_hidden("chain", before, _chain_combo)


def add_air_time(dt):
    _ensure()
    state["air_time"] += max(0.0, dt)
    old_best = state["best"].get("sky", 0.0)
    new_best = max(old_best, state["air_time"])
    state["best"]["sky"] = new_best
    before = _level(old_best, TIERS["sky"])
    after = _level(new_best, TIERS["sky"])
    _notify("sky", TIERS["sky"], before, after)
    if after != before:
        _save()


def add_idle(dt):
    _ensure()
    before = state["idle"]
    state["idle"] += max(0.0, dt)
    _notify_hidden("statue", before, state["idle"])


def reset_idle():
    """Standing still must be uninterrupted: moving resets the statue timer."""
    _ensure()
    if state["idle"]:
        state["idle"] = 0.0


def update_selfhit(age_seconds):
    """Your own old candy (thrown >= threshold seconds ago) blasted you."""
    _ensure()
    age_seconds = float(age_seconds)
    if age_seconds < HIDDEN_TIERS["selfhit"]:
        return
    before = state["selfhit"]
    if age_seconds > before:
        state["selfhit"] = age_seconds
        _notify_hidden("selfhit", before, age_seconds)


def update_streak(seconds):
    _ensure()
    seconds = float(seconds)
    if seconds <= state["streak"]:
        return
    before = state["streak"]
    state["streak"] = seconds
    _notify_hidden("streak", before, seconds)


def update_fails(count):
    """Falls at the same spot (per run)."""
    _ensure()
    count = int(count)
    if count <= state["fails"]:
        return
    before = state["fails"]
    state["fails"] = count
    _notify_hidden("fails", before, count)


def update_platforms(count):
    """Different platforms the player has stood on this run."""
    _ensure()
    count = int(count)
    if count <= state["platforms"]:
        return
    state["platforms"] = count
    old_best = state["best"].get("platforms", 0.0)
    new_best = max(old_best, count)
    state["best"]["platforms"] = new_best
    before = _level(old_best, TIERS["platforms"])
    after = _level(new_best, TIERS["platforms"])
    _notify("platforms", TIERS["platforms"], before, after)
    if after != before:
        _save()


def take_new():
    out = NOTIFY[:]
    NOTIFY[:] = []
    return out


def reset_run():
    _ensure()
    global _last_explosion_time
    state["candies"] = 0
    state["air_throws"] = 0
    state["chains"] = 0
    state["air_time"] = 0.0
    state["idle"] = 0.0
    state["selfhit"] = 0.0
    state["streak"] = 0.0
    state["platforms"] = 0
    state["fails"] = 0
    _last_explosion_time = 0.0
    _chain_combo = 0
    _save()


def clears():
    _ensure()
    return state["clears"]


def max_height():
    _ensure()
    return state["max_height"]


# ---------------------------------------------------------------- helpers
def _value(kind):
    _ensure()
    current = {
        "height": state["max_height"], "clears": state["clears"],
        "candy": state["candies"], "air": state["air_throws"],
        "sky": state["air_time"], "platforms": state["platforms"],
        "statue": state["idle"], "selfhit": state["selfhit"],
        "fails": state["fails"],
        "streak": state["streak"], "chain": state["chains"],
    }[kind]
    if kind in HIDDEN_TIERS:
        return max(current, state["unlocked"].get(kind, 0.0))
    return max(current, state["best"].get(kind, 0.0))


def _fmt_value(kind, value):
    """Heights are stored in px but shown in metres."""
    if kind == "height":
        return int(round(value)) // PX_PER_M
    if kind == "selfhit":
        return ("%.1f" % float(value)).rstrip("0").rstrip(".")
    return int(round(value))


def level(kind):
    """Rank level of a normal achievement (0..5); hidden are 0 or 1."""
    _ensure()
    if kind in HIDDEN_TIERS:
        return 1 if kind in state["unlocked"] else 0
    return _level(_value(kind), TIERS[kind])


def is_hidden(kind):
    return kind in HIDDEN_ORDER


def rank_name(level_index, lang="en"):
    """Rank name for level 1..5 (0 -> locked)."""
    l = L.get(lang) or L["en"]
    if level_index <= 0:
        return l["locked"]
    return l["ranks"][min(level_index, 5) - 1]


def achievement_name(kind, lang="en"):
    l = L.get(lang) or L["en"]
    return l["names"][kind]


def req_text(kind, rank_index, lang="en"):
    """Requirement for rank rank_index (0..4), or the single hidden condition."""
    _ensure()
    l = L.get(lang) or L["en"]
    if kind in HIDDEN_TIERS:
        return l["req"][kind].format(v=_fmt_value(kind, HIDDEN_TIERS[kind]))
    tier = TIERS[kind][rank_index]
    return l["req"][kind].format(v=_fmt_value(kind, tier))


def progress_text(kind, lang="en"):
    l = L.get(lang) or L["en"]
    return l["prog"][kind].format(c=_fmt_value(kind, _value(kind)))


def describe(kind, tier, lang="en"):
    """Localised (title, detail) pair for an unlock notification."""
    l = L.get(lang) or L["en"]
    if kind in HIDDEN_TIERS:
        detail = l["req"][kind].format(v=_fmt_value(kind, HIDDEN_TIERS[kind]))
        return l["names"][kind], detail
    tiers = TIERS[kind]
    rank = tiers.index(tier) + 1
    detail = "%s · %s" % (l["ranks"][rank - 1],
                          l["req"][kind].format(v=_fmt_value(kind, tier)))
    return l["names"][kind], detail


def get_list(lang="en"):
    """Rows for the achievements screen, all ten achievements."""
    l = L.get(lang) or L["en"]
    rows = []
    for kind in ALL_ORDER:
        lvl = level(kind)
        hidden = is_hidden(kind)
        hidden_locked = hidden and lvl == 0
        max_lvl = 1 if hidden else 5
        rows.append({
            "id": kind,
            "name": l["names"][kind] if not hidden_locked else "???",
            "hidden": hidden,
            "locked": hidden_locked,
            "level": lvl,
            "max_level": max_lvl,
            "unlocked": lvl > 0,
            "rank": rank_name(lvl, lang) if not hidden else "",
            "progress": progress_text(kind, lang),
            "next": "" if hidden else (
                l["next"].format(n=req_text(kind, lvl, lang)) if lvl < 5 else l["max"]),
        })
    return rows
