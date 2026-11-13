#!/usr/bin/env python3
"""Reads the app's own data and writes content/practice.json, the single source for the practice library
(scripts/practice_pages.py). Run it again whenever the app's exercises, speaking modes or brain games change:

  python3 scripts/extract-practice.py [path to app/web/src]     default: ../app/web/src

It only reads the app repo. What it takes:
  features/rehab/exercises.ts            ids, names, tracking mode, body part, the instruction shown on screen
  lib/exerciseMeta.ts                    body area, level 1 to 3, seated or standing, one side at a time
  lib/limits.ts                          free-plan exercise ids, free speaking levels, free brain level
  features/rehab/engine/*Calculator.js   the cue words shown while counting, what must be in view, the lean check
  features/speech/{labels,levels,cues}.ts  mode names, level count, pass mark
  features/brain/{BrainHome.tsx,cognitive.ts,logic.ts}  game names, groups, what each level sets
  lib/i18n.{tw,cn,ja,es,de,fr}.ts        the app's own wording in each language (keyed by the Cantonese string)
Site language -> app language: en en, yue zh, zh-hant tw, zh-hans cn, ja, es, de, fr.
A phrase the app has no translation for is listed under "untranslated" and falls back to English on the page."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "app" / "web" / "src"
LANGS = {"en": "en", "yue": "zh", "zh-hant": "tw", "zh-hans": "cn", "ja": "ja", "es": "es", "de": "de", "fr": "fr"}
rd = lambda p: (SRC / p).read_text()

# ---- dictionaries
PAIR = re.compile(r'^\s*("(?:[^"\\]|\\.)*"):\s*("(?:[^"\\]|\\.)*"),?')
DICT = {}
for code in ("tw", "cn", "ja", "es", "de", "fr"):
    d = {}
    for line in rd(f"lib/i18n.{code}.ts").splitlines():
        m = PAIR.match(line)
        if m:
            d[json.loads(m.group(1))] = json.loads(m.group(2))
    DICT[code] = d
UNTRANSLATED = {}


def _pattern(d, zh):
    """Keys with {0}, {1}: match them as patterns, as the app's matcher does."""
    for k, v in d.items():
        if "{0}" not in k:
            continue
        rx = "^" + "(.*?)".join(re.escape(p) for p in re.split(r"\{\d+\}", k)) + "$"
        m = re.match(rx, zh)
        if m:
            order = [int(x) for x in re.findall(r"\{(\d+)\}", k)]
            got = dict(zip(order, m.groups()))
            v = re.sub(r"\{(\d+):([^|}]*)\|([^}]*)\}", lambda q: q.group(2) if got.get(int(q.group(1))) == "1" else q.group(3), v)
            return re.sub(r"\{(\d+)\}", lambda q: got.get(int(q.group(1)), ""), v)
    return None


def tr(en, zh):
    """One app phrase in every site language."""
    out = {}
    for site, app in LANGS.items():
        if app == "en":
            out[site] = en
        elif app == "zh":
            out[site] = zh
        else:
            v = DICT[app].get(zh)
            if v is None:
                v = _pattern(DICT[app], zh)
            if v is None:
                UNTRANSLATED.setdefault(site, []).append(en)
                v = zh if app == "tw" else en
            v = re.sub(r"\{\d+:([^|}]*)\|[^}]*\}", r"\1", v)
            if app in ("tw", "cn"):
                v = v.replace("朱古力", "巧克力")
            out[site] = v
    return out


slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
unq = lambda s: s.replace("\\'", "'")

# ---- exercises
STR = r"'((?:[^'\\]|\\.)*)'"
EX = re.compile(rf"ex\('(\w+)', {STR}, {STR}, '(\w+)', '(\w+)', \{{([^}}]*)\}}, (\d+), \{{ en: {STR}, zh: {STR} \}}\)")
META = dict((m.group(1), m) for m in re.finditer(r"^\s*(\w+): m\(\[([^\]]*)\], (\d), (true|false)(?:, (true))?\)", rd("lib/exerciseMeta.ts"), re.M))
limits = rd("lib/limits.ts")
FREE = re.findall(r"'(\w+)'", re.search(r"FREE_EXERCISE_IDS[^=]*= \[([^\]]*)\]", limits).group(1))
pose, hand = rd("features/rehab/engine/PoseCalculator.js"), rd("features/rehab/engine/HandCalculator.js")
FB = {}
for m in re.finditer(rf"'([GF]\d+)': \{{[^\n]*\n\s*en: \{{ progress: {STR}, hold: {STR}, done: {STR}, relax: {STR} \}},\s*\n\s*zh: \{{ progress: {STR}, hold: {STR}, done: {STR}, relax: {STR} \}}", pose + hand):
    g = [unq(x) for x in m.groups()[1:]]
    FB[m.group(1)] = {"progress": (g[0], g[4]), "hold": (g[1], g[5]), "relax": (g[3], g[7])}


def cases(src, fn_start, ret):
    """ids listed in the `case` lines just above a `return <ret>` inside requiredLandmarks."""
    body = src[src.index(fn_start):]
    body = body[:body.index("default:")]
    block = body[:body.index(ret)]
    last = block.rsplit("return", 1)[-1] if "return" in block else block
    return re.findall(r"case '(\w+)'", last)


SHOULDERS = cases(pose, "requiredLandmarks(exerciseId)", "return shoulders;")
LEGS = cases(pose, "requiredLandmarks(exerciseId)", "return hips.concat([L.LEFT_KNEE, L.RIGHT_KNEE]);")
LEGS_ANKLES = cases(pose, "requiredLandmarks(exerciseId)", "return hips.concat([L.LEFT_KNEE, L.RIGHT_KNEE, L.LEFT_ANKLE, L.RIGHT_ANKLE]);")
SPINE = re.findall(r"'(\w+)'", re.search(r"requiresStraightSpine = \[([^\]]*)\]", pose).group(1))
assert SHOULDERS and LEGS and LEGS_ANKLES and SPINE, "engine layout changed: check requiredLandmarks in PoseCalculator.js"

exercises = []
for m in EX.finditer(rd("features/rehab/exercises.ts")):
    eid, en, zh, mode, part, thr, _xp, ins_en, ins_zh = m.groups()
    en, ins_en = unq(en), unq(ins_en)
    mm = META[eid]
    view = "hand" if mode == "hand" else "shoulders" if eid in SHOULDERS else "legs" if eid in LEGS else "legs_ankles" if eid in LEGS_ANKLES else "body"
    fb = FB.get(eid)
    exercises.append({
        "id": eid, "slug": slug(en), "name": tr(en, zh), "instruction": tr(ins_en, ins_zh), "mode": mode, "bodyPart": part,
        "areas": re.findall(r"'(\w+)'", mm.group(2)), "level": int(mm.group(3)), "seated": mm.group(4) == "true", "oneSided": bool(mm.group(5)),
        "free": eid in FREE, "hold": "holdTime" in thr, "view": view, "leanCheck": eid in SPINE,
        "cues": {k: tr(*v) for k, v in fb.items()} if fb else None,
    })
assert len(exercises) == len(META) and len({e["slug"] for e in exercises}) == len(exercises), "exercise list and metadata disagree"

AREA_SLUG = {"arm_shoulder": "arm-and-shoulder", "hand": "hand-and-fingers", "legs": "legs-and-walking", "balance": "balance", "neck_back": "neck-and-back"}
areas = []
for m in re.finditer(rf"^\s*(\w+): \{{ en: {STR}, zh: {STR} \}},", rd("lib/exerciseMeta.ts"), re.M):
    areas.append({"id": m.group(1), "slug": AREA_SLUG[m.group(1)], "title": tr(unq(m.group(2)), m.group(3))})
assert [a["id"] for a in areas] == re.findall(r"'(\w+)'", re.search(r"AREAS: Area\[\] = \[([^\]]*)\]", rd("lib/exerciseMeta.ts")).group(1))

# ---- speaking
labels = rd("features/speech/labels.ts")


def switch(fn):
    body = labels[labels.index(f"function {fn}"):]
    body = body[:body.index("\n}\n")]
    return {m.group(1): (unq(m.group(2)), m.group(3)) for m in re.finditer(rf"case '(\w+)':\s*return tr\({STR}, {STR}\)", body)}


names, purposes = switch("modeLabel"), switch("modePurpose")
MODES = ["pronunciation", "naming", "sentence", "completion", "listening", "match"]
assert set(MODES) == set(names), "speaking modes changed"
num = lambda src, name: int(re.search(rf"{name} = (\d+)", src).group(1))
levels_ts, cues_ts = rd("features/speech/levels.ts"), rd("features/speech/cues.ts")
speech = {
    "levels": num(levels_ts, "LEVEL_COUNT"), "unit": num(levels_ts, "UNIT_SIZE"), "free_max_level": num(limits, "FREE_SPEECH_MAX_LEVEL"), "pass_pct": num(cues_ts, "PASS_PCT"),
    "modes": [{"id": k, "slug": slug(names[k][0]), "name": tr(*names[k]), "purpose": tr(*purposes[k])} for k in MODES],
}

# ---- brain games
home = rd("features/brain/BrainHome.tsx")
groups = []
for g in re.finditer(rf"title: tr\({STR}, {STR}\),\s*\n\s*hint: tr\({STR}, {STR}\),\s*\n\s*games: \[(.*?)\n\s*\],", home, re.S):
    games = [{"id": m.group(1), "slug": slug(unq(m.group(2))), "name": tr(unq(m.group(2)), m.group(3)), "body": tr(unq(m.group(4)), m.group(5))}
             for m in re.finditer(rf"to: '/brain/(\w+)',[^\n]*?title: tr\({STR}, {STR}\), body: tr\({STR}, {STR}\)", g.group(5))]
    groups.append({"slug": slug(unq(g.group(1))), "title": tr(unq(g.group(1)), g.group(2)), "hint": tr(unq(g.group(3)), g.group(4)), "games": games})
assert sum(len(g["games"]) for g in groups) == 6, "brain game list changed"
cog, logic = rd("features/brain/cognitive.ts"), rd("features/brain/logic.ts")


def table(src, name):
    body = src[src.index(f"export const {name}"):]
    body = body[:body.index("\n}")]
    out = {}
    for m in re.finditer(r"^\s*(\w+): \{([^}]*)\}", body, re.M):
        out[m.group(1)] = {k: (json.loads(v.replace("'", '"')) if v.strip().startswith("[") else v.strip() == "true" if v.strip() in ("true", "false") else int(v))
                           for k, v in re.findall(r"(\w+): (\[[^\]]*\]|[\w.]+)", m.group(2))}
    return out


brain = {"groups": groups, "free_max_level": num(limits, "FREE_BRAIN_MAX_LEVEL"),
         "span": table(cog, "SPAN_CONFIG"), "pairs": table(cog, "PAIRS_CONFIG"), "trail": table(cog, "TRAIL_CONFIG"),
         "math": table(logic, "MATH_DIFFICULTY"), "target": table(logic, "LEVEL_CONFIG")}

# ---- short phrases the pages quote from the app, in the app's own words
PHRASES = {
    "easy": ("Easy", "簡單"), "medium": ("Medium", "中等"), "hard": ("Hard", "困難"),
    "listen_again": ("Listen again, slowly", "再聽一次，慢啲"), "first_sound": ("First sound", "第一個音"), "the_word": ("The word", "個字"), "the_sentence": ("The sentence", "句子"),
    "say_with_me": ("Listen, then say it with me", "聽完，同我一齊讀"), "build_with_me": ("Listen, then build it with me.", "聽完，同我一齊砌。"), "show_pron": ("Show pronunciation", "顯示發音"),
    "two_pictures": ("Two pictures are left.", "剩返兩幅圖。"), "two_words": ("Two words are left.", "剩返兩個字。"), "starts_with": ("Starts with the sound shown.", "以顯示嘅音開頭。"),
    "answer_marked": ("The answer is marked.", "已標示答案。"), "listen_question": ("Listen to the question again", "再聽一次條問題"),
    "no_camera": ("Do it without the camera", "唔用鏡頭做"), "tap_screen": ("Tap the screen", "㩒螢幕"), "use_camera": ("Use the camera", "用鏡頭"),
    "math_simple": ("Small numbers, + and −", "細啲嘅數，加減"), "math_medium": ("Bigger numbers, + and −", "大啲嘅數，加減"), "math_hard": ("Adds times (×)", "加埋乘數 (×)"),
    "few": ("Only a few on screen", "螢幕上面少啲"), "more": ("More on screen", "螢幕上面多啲"),
    "set_of_questions": ("A set of questions", "一組題目"), "keep_going": ("Keep going", "持續練習"), "pick_named": ("Pick what I ask for", "揀我講嘅嘢"),
    "slow": ("Slow", "慢速"), "normal": ("Normal", "正常"),
}
phrases = {k: tr(*v) for k, v in PHRASES.items()}
for lv in "123":
    c = brain["span"][lv]
    phrases[f"span_{lv}"] = tr(f"{c['cells']} squares, starts with {c['startSpan']}", f"{c['cells']} 個方格，由 {c['startSpan']} 個開始")
    c = brain["pairs"][lv]
    phrases[f"pairs_{lv}"] = tr(f"{c['pairs']} pairs, {c['pairs'] * 2} cards", f"{c['pairs']} 對，{c['pairs'] * 2} 張牌")
    c = brain["trail"][lv]
    phrases[f"trail_{lv}"] = tr(f"{c['count']} items, numbers and letters", f"{c['count']} 個，數字加字母") if c["alternating"] else tr(f"Numbers 1 to {c['count']}", f"數字 1 至 {c['count']}")
    c = brain["target"][lv]
    phrases[f"target_{lv}"] = tr(f"{c['items']} things, {c['targets']} to find", f"{c['items']} 樣嘢，要搵 {c['targets']} 個")
    phrases[f"level_{lv}"] = tr(f"Level {lv}", f"第 {lv} 級")

out = {"_comment": "Written by scripts/extract-practice.py from the app's own data. Do not edit by hand: run the script again.",
       "exercises": exercises, "areas": areas, "speech": speech, "brain": brain, "phrases": phrases,
       "untranslated": {k: sorted(set(v)) for k, v in UNTRANSLATED.items()}}
(ROOT / "content" / "practice.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print(f"{len(exercises)} exercises ({sum(e['free'] for e in exercises)} free), {len(areas)} areas, {len(speech['modes'])} speaking modes, {sum(len(g['games']) for g in groups)} brain games")
for k, v in out["untranslated"].items():
    print(f"no app translation ({k}): {len(v)}: {v}")
