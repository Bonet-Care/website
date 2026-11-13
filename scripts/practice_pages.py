"""The practice library, built by build-site.py in every language from content/practice.json (the app's own data,
written by scripts/extract-practice.py):

  /practice                    the hub: Move by body area (with seated, standing and free-plan lists), Speak, Think
  /practice/move/<slug>        one page per exercise
  /practice/speak/<slug>       one page per kind of speaking practice
  /practice/think/<slug>       one page per brain game
  /practice/area/<slug>        one page per body area

Names, instructions, cue words, level names and numbers come from practice.json, so they are the app's own wording in each
language. Everything else is copy written here in English: content/practice.yue.json holds the Cantonese gloss and
strings/<lang>.json the other languages, exactly as for the pages in seo_pages.py. A missing string fails --strict.

Rules for this copy: Bonet is a practice tool. Describe the movement and the practice only. Never say an exercise is for a
condition, and never claim treatment, recovery, improvement or strength. No sets or repetition prescriptions. CAM (what the
camera follows) must stay true to features/rehab/engine in the app: change it only together with the engine."""
import json
import unicodedata
import parts
from parts import APP, FACTS, LANG_COUNT, LANGS, ROOT, mk, pre, u
if not hasattr(parts, "FLAGS_OFF"):
    parts.FLAGS_OFF = set()  # run on its own (see the end of this file)
import seo_pages
from seo_pages import DEMO_ALT, DISCLAIMER, LANG_LINE, _crumbs, _fill, _write

DATA = json.loads((ROOT / "content" / "practice.json").read_text())
_yue = ROOT / "content" / "practice.yue.json"
YUE = json.loads(_yue.read_text()) if _yue.exists() else {}
USED = []  # every English string asked for, in order (python3 scripts/practice_pages.py prints them for translators)

EX = DATA["exercises"]
EX_BY_ID = {e["id"]: e for e in EX}
AREAS = DATA["areas"]
AREA_BY_ID = {a["id"]: a for a in AREAS}
SPEECH = DATA["speech"]
MODES = SPEECH["modes"]
BRAIN = DATA["brain"]
GAMES = [dict(g, group=grp) for grp in BRAIN["groups"] for g in grp["games"]]
PH = DATA["phrases"]
assert len(EX) == FACTS["exercises"] and sum(e["free"] for e in EX) == FACTS["free_exercises"] and SPEECH["levels"] == FACTS["speaking_levels"], \
    "content/practice.json and content/facts.json disagree: run scripts/extract-practice.py and check facts.json"

move_slug = lambda e: f"practice/move/{e['slug']}"
speak_slug = lambda m: f"practice/speak/{m['slug']}"
think_slug = lambda g: f"practice/think/{g['slug']}"
area_slug = lambda a: f"practice/area/{a['slug']}"
SLUGS = ["practice"] + [area_slug(a) for a in AREAS] + [move_slug(e) for e in EX] + [speak_slug(m) for m in MODES] + [think_slug(g) for g in GAMES]
LOCAL_SITEMAP = ([("practice", "0.8")] + [(area_slug(a), "0.7") for a in AREAS] + [(move_slug(e), "0.6") for e in EX]
                 + [(speak_slug(m), "0.6") for m in MODES] + [(think_slug(g), "0.6") for g in GAMES])
in_area = lambda a: [e for e in EX if a["id"] in e["areas"]]

# Strings that already exist on other pages (same English, so the same translation is used).
REUSE = {
    "The count is an estimate. Light, camera angle and loose clothing can change it.": "次數只係估算。光線、鏡頭角度同鬆身衫都會影響佢。",
    "Camera video is read on your device. It is never recorded or uploaded.": "鏡頭影像只喺你部機讀取，唔會錄低或者上載。",
    "Do not rely on the camera to keep you safe. It can miss a loss of balance.": "唔好靠鏡頭保障安全。佢可能留意唔到你失平衡。",
    "Each type has {levels} levels, so you can begin where it feels comfortable and move up slowly. Items you found hard come back later for review.": "每種練習有 {levels} 級，你可以由覺得舒服嘅級別開始，慢慢升上去。未熟嘅題目之後會再出現俾你複習。",
    "You get a hint. Hints grow one step at a time, so you get just enough help to keep going. Using hints is part of practice, not a mistake.": "你會有提示。提示一步一步加大，俾你啱啱夠嘅幫助繼續落去。用提示係練習嘅一部分，唔係做錯。",
    "Recognition runs on your device where the device supports it. Otherwise it is handled by Apple (on iPhone and iPad) or Google (on the web, for several languages). Bonet keeps the recognised text and the measures. It does not keep voice recordings. See <a href=\"/what-bonet-tracks\">what Bonet tracks</a>.":
        "部機支援嘅話，辨識會喺你部機進行。否則由 Apple（iPhone 同 iPad）或者 Google（網頁版，部分語言）處理。哥基健動只保留認到嘅文字同量度結果，唔保留錄音。詳情請睇<a href=\"/what-bonet-tracks\">哥基健動記錄啲乜</a>。",
    "What to know before you start": "開始之前要知嘅事", "More about Bonet": "更多關於哥基健動", "Frequently asked questions": "常見問題",
    "Move": "運動", "Speak": "說話", "Think": "腦力", "Languages": "語言",
    DISCLAIMER[0]: DISCLAIMER[1], LANG_LINE[0]: LANG_LINE[1], DEMO_ALT["move"][0]: DEMO_ALT["move"][1],
}

# What the camera follows for each exercise, in plain words. Source: processExercise() in PoseCalculator.js and HandCalculator.js.
CAM = {
    "G01": "The camera compares the height of each ankle with the knee. When one foot is lifted high enough, a timer starts, and it stops when the foot comes down. A hold of several seconds counts as one repetition.",
    "G02": "The camera follows the angle between your body and your upper arms as both arms rise in front of you. It uses the average of the two arms.",
    "G10": "The camera follows the angle between your body and your upper arms as both arms rise in front of you. It uses the average of the two arms.",
    "G03": "The camera follows the angle between your body and your upper arm as the arm rises in front of you. It reads whichever arm is lifted higher.",
    "G04": "The camera follows the angle between your body and your upper arms as both arms rise out to the sides. It uses the average of the two arms.",
    "G11": "The camera follows the angle between your body and your upper arm as the arm rises out to the side. It reads whichever arm is lifted higher.",
    "G05": "The camera follows the angle at both elbows, from shoulder to elbow to wrist, as your arms straighten. It uses the average of the two arms.",
    "G06": "The camera follows the angle at the elbow, from shoulder to elbow to wrist. It reads whichever arm is straighter.",
    "G07": "The camera follows how far apart your wrists move as your hands turn outward. It sees a flat picture, so this is only a rough stand-in for the turn of the shoulder.",
    "G08": "The camera follows how far your head moves to the left or right of the middle of your hips as you lean.",
    "G12": "The camera follows how far your head moves to the left or right of the middle of your hips as you shift your weight.",
    "G13": "The camera follows how high each knee lifts compared with the ankle as you march. It reads whichever knee is higher.",
    "G09": "The camera follows the lean of your upper body, from hips to shoulders, as you bend forward.",
    "G14": "The camera compares the height of your hips with your knees. When your hips rise clearly above your knees, it reads that as standing. When they come back down, it reads that as sitting.",
    "G15": "The camera follows the angle at the knee, from hip to knee to ankle. It reads whichever leg is straighter.",
    "G16": "The camera follows how far your heels lift compared with your toes. This is a small movement on camera, so the count is more sensitive to the camera angle than in other exercises.",
    "G17": "The camera follows the distance between each ear and the shoulder below it as your head tilts.",
    "G18": "The camera follows how far your nose moves to the left or right of the middle of your shoulders as your head turns.",
    "G19": "The camera follows the distance between your nose and your shoulders. A chin tuck is a small movement, and from the front the camera may not always pick it up.",
    "G20": "The camera follows how far the middle of your shoulders moves sideways compared with the middle of your hips as you twist.",
    "G21": "The camera follows how much the line between your two shoulders tilts as you bend to the side.",
    "G22": "The camera follows the lean of your upper body, from hips to shoulders, as you lean back. From the front this is hard for a camera to see, so the count may be less steady.",
    "G23": "The camera follows the distance between your two shoulders, which gets a little smaller as you squeeze. This is a small movement on camera, so the count is more sensitive than in other exercises.",
    "F01": "The camera follows the distance between the tip of your thumb and the tip of your index finger.",
    "F02": "The camera follows how far your fingertips are from your wrist: close for a fist, far for an open hand.",
    "F03": "The camera checks which finger your thumb is touching. One round is counted when the thumb has touched the index, middle, ring and little finger in that order, lifting off between touches. A touch on the wrong finger is ignored. It is not counted against you.",
    "F04": "The camera follows the distance between the tip of your thumb and the base of your little finger.",
    "F05": "The camera follows the angle of your hand as the wrist bends up or down. How the hand is turned toward the camera changes the reading.",
    "F06": "The camera follows the gaps between neighbouring fingertips, which get wider as the fingers spread.",
    "F07": "The camera follows how far the hand tilts to either side at the wrist. How the hand is turned toward the camera changes the reading.",
    "F08": "The camera follows how far one fingertip rises above its knuckle while the other fingers stay down. It works best with the hand flat on a table.",
    "F09": "The camera follows the bend at the middle joint of the four fingers.",
    "F11": "The camera follows the distance between the tip of your thumb and the tip of your little finger.",
    "F13": "The camera follows how close your fingertips come to your palm while the big knuckles stay straight.",
}
assert set(CAM) == set(EX_BY_ID), "CAM must have one entry per exercise"
RULE = {
    "pose": "A repetition is counted when you reach the position, hold it for about one second, and then come back to the start. The next repetition begins after you have returned.",
    "hand": "A repetition is counted when you reach the position and hold it for a moment. The next repetition begins after you have opened or relaxed the hand again.",
}
NO_RULE = {"G01", "F03"}  # their CAM text already says how a repetition is counted
NO_CUES = {"F03"}  # its cue words name the next finger, so they are not a fixed order
FULL_BODY = {"G01", "G16"}  # counted from the ankles or heels, so the feet must be in the picture
VIEW = {
    "shoulders": "For this exercise the camera needs to see your upper body, with both shoulders in the picture.",
    "body": "For this exercise the camera needs to see your upper body down to your hips.",
    "legs": "For this exercise the camera needs to see your hips, knees and feet.",
    "full": "For this exercise the camera needs to see your whole body, from shoulders to feet.",
    "hand": "For this exercise the camera needs to see one hand clearly.",
}
view_of = lambda e: "full" if e["id"] in FULL_BODY else "legs" if e["view"].startswith("legs") else e["view"]

AREA_INTRO = {
    "arm_shoulder": "These exercises move the shoulders and elbows: lifting one arm or both arms forward or out to the side, turning the hands outward with the elbows at your sides, and straightening the elbow. In two of them the hands are clasped, so both arms move together.",
    "hand": "These exercises are followed with hand tracking: pinching, making a fist, spreading and curling the fingers, touching the thumb to each finger in turn, lifting one finger at a time, and moving the wrist up and down or side to side.",
    "legs": "These exercises move the legs: marching on the spot, standing up from a chair and sitting down again, straightening one knee while seated, and rising onto the toes.",
    "balance": "These exercises shift your weight: standing on one leg, leaning from side to side while seated or standing, and rising onto the toes. Most of them need standing, so stand next to something sturdy you can hold.",
    "neck_back": "These exercises move the neck and the back: tilting and turning the head, tucking the chin, bending forward, to the side and gently back, twisting the upper body while seated, and squeezing the shoulder blades together. All of them can be done seated.",
}
assert all(e["seated"] for e in in_area(AREA_BY_ID["neck_back"])) and sum(not e["seated"] for e in in_area(AREA_BY_ID["balance"])) * 2 > len(in_area(AREA_BY_ID["balance"])), "AREA_INTRO no longer matches the data"

# ---- speaking practice: what you do, the hint steps (features/speech/cues.ts cueSteps, labels from modes.tsx), what is recorded
SPEAK = {
    "pronunciation": {
        "tail": "read-aloud speaking practice at home",
        "do": ["A word or a short phrase is shown on the screen. You say it aloud into the microphone. The app writes down what it heard and compares it with what was shown.",
               "If you want to see how it is read, tap <q>{show_pron}</q>. At higher levels the items get longer, up to whole sentences."],
        "hints": ["<q>{listen_again}</q>: the item is played again at a slower speed.", "<q>{first_sound}</q>: the first sound is shown and played, when the item is longer than one sound.",
                  "The pronunciation guide is shown, when it is not already on screen.", "<q>{say_with_me}</q>: the app says it and you say it together."],
        "measure": "spoken_full",
    },
    "naming": {
        "tail": "picture naming practice at home",
        "do": ["A picture is shown and the app asks you to say its name. You answer aloud into the microphone.",
               "Common ways of saying the same thing are accepted, so there is often more than one right answer."],
        "hints": ["<q>{listen_question}</q>: the question is played again.", "<q>{first_sound}</q>: the first sound of the name is shown and played.", "A clue about what kind of thing it is, when the item has one.",
                  "<q>{the_word}</q>: the written name is shown.", "<q>{say_with_me}</q>: the app says the name and you say it together."],
        "measure": "spoken",
    },
    "sentence": {
        "tail": "sentence building practice at home",
        "do": ["The words of a sentence are shown as tiles in mixed order. You tap the tiles to put the sentence together, then check it.",
               "If it is not right yet, the app keeps the part that is right and gives a hint. When the sentence is built, you say it aloud."],
        "hints": ["The idea of the sentence is read aloud, when the item has one.", "The next word is highlighted and read aloud.", "<q>{the_sentence}</q>: the whole sentence is shown.",
                  "<q>{build_with_me}</q> The app reads the sentence and you build it along."],
        "measure": "spoken_full",
    },
    "completion": {
        "tail": "sentence completion practice at home",
        "do": ["A sentence with one word missing is shown, with several words to choose from. You pick the word that fits.",
               "When the sentence is complete, you say the whole sentence aloud."],
        "hints": ["The sentence is played again, slowly.", "<q>{starts_with}</q>", "<q>{two_words}</q> The right word and one other stay.", "<q>{answer_marked}</q>"],
        "measure": "spoken_full",
    },
    "listening": {
        "tail": "hear a word and pick the picture",
        "do": ["The app says a word or a short phrase and shows several pictures. You tap the picture that matches.",
               "You can play it again and choose between two speeds, <q>{slow}</q> and <q>{normal}</q>. You do not need to speak in this practice."],
        "hints": ["<q>{listen_again}</q>: it is played again at a slower speed.", "<q>{two_pictures}</q> The right picture and one other stay."],
        "measure": "choice",
    },
    "match": {
        "tail": "match pictures and words from memory",
        "do": ["Cards are shown for a few seconds so you can memorise them: each picture has a matching card with its word. Then the cards turn over.",
               "You turn over two cards at a time to find the pairs. A wrong pair turns back over and you try again. You do not need to speak in this practice."],
        "hints": None,
        "measure": "cards",
    },
}
assert set(SPEAK) == {m["id"] for m in MODES}
MEASURE = {
    "spoken_full": (["After you speak, the app shows a few plain numbers about that try:"],
                    ["how many of the words or characters it heard;", "your pace, as words, characters or sounds a minute;", "how long you took to start;", "how many short pauses there were."],
                    ["These are practice indicators, not a test or an assessment. Recognition can miss words you did say, so a low number may be the app's mistake and not yours."]),
    "spoken": (["The app checks whether it heard the name of the picture. It records how many tries you took and which hints you used."], [], []),
    "choice": (["Nothing is taken from the microphone in this practice. The app records which picture you chose, how many tries it took and which hints you used."], [], []),
    "cards": (["Nothing is taken from the microphone in this practice. The app records that you finished the set and how many wrong pairs you turned over."], [], []),
}

# ---- brain games: what you do, how you answer, what the app shows afterwards
THINK = {
    "span": {"do": ["A grid of squares is shown. Some of the squares light up, one after another. When it is your turn, you tap the same squares in the same order.",
                    "When you get a list right, the next one is one square longer. After a miss you get a new list of the same length. The game ends after two misses in a row, or when you reach the longest list for that level."],
             "input": "touch", "shown": "the longest list you remembered, the seconds per tap and the number of wrong taps"},
    "pairs": {"do": ["Cards lie face down. You turn over two at a time. If they are the same, they stay open. If not, they turn back over and you try again.",
                     "The game ends when you have found every pair, or when the time for that level runs out."],
              "input": "touch", "shown": "the pairs you found, the time and the number of tries"},
    "trail": {"do": ["Numbers are scattered over the screen. You tap them in order, from the smallest to the biggest. The app shows which one comes next.",
                     "On the hardest level, numbers and letters take turns: a number, then a letter, then the next number."],
              "input": "touch", "shown": "how many you tapped right, the time and the number of wrong taps"},
    "dimsum": {"do": ["Pictures of dim sum appear on the screen. Bonet names one, and you pick it before the time for that round runs out.",
                      "There are three ways to play: <q>{pick_named}</q>, picking every dumpling on the screen, or <q>{keep_going}</q>, which runs for a few minutes."],
               "input": "both", "shown": "your points and how many rounds you got right"},
    "fruit": {"do": ["Pictures of fruit appear on the screen. Bonet names one, and you pick it before the time for that round runs out.",
                     "There are three ways to play: <q>{pick_named}</q>, picking every apple on the screen, or <q>{keep_going}</q>, which runs for a few minutes."],
              "input": "both", "shown": "your points and how many rounds you got right"},
    "math": {"do": ["A sum is shown with several answers. You work it out and pick the right answer before the time for that question runs out.",
                    "You can do <q>{set_of_questions}</q>, one at a time, or choose <q>{keep_going}</q> and practise for a few minutes."],
             "input": "both", "shown": "your points and how many questions you got right"},
}
assert set(THINK) == {g["id"] for g in GAMES}
INPUT = {"touch": "You play by tapping the screen.",
         "both": "You can play in two ways: <q>{tap_screen}</q>, or <q>{use_camera}</q>. With the camera you hold your hand over an answer for a moment and it is chosen. The camera picture stays on your device."}
GROUP_TAIL = {"memory": "a short memory game for daily practice", "attention": "a short attention game for daily practice", "thinking": "a short thinking game for daily practice"}


# ------------------------------------------------------------------ helpers
def _tools(lang):
    T = mk(lang)

    def t(en, **kw):
        if en not in USED:
            USED.append(en)
        yue = YUE.get(en, REUSE.get(en))
        if yue is None:
            parts.MISSING.setdefault("yue", set()).add(en)
        s = _fill(T(en, yue), lang)
        for k, v in kw.items():
            s = s.replace("{" + k + "}", str(v))
        for k in PH:  # the app's own words
            if "{" + k + "}" in s:
                s = s.replace("{" + k + "}", PH[k][lang])
        return s
    return t


CJK = ("yue", "zh-hant", "zh-hans", "ja")
_sep = lambda lang: "：" if lang in CJK else "\u00a0: " if lang == "fr" else ": "  # between a linked name and its one-line description


def _width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def _fit(*cands):
    """The first title that fits a search result line, else the shortest."""
    return next((c for c in cands if _width(c) <= 66), min(cands, key=_width))


def _trail(lang, links):
    return '<p class="note">' + " / ".join(f'<a href="{h}">{x}</a>' for h, x in links) + "</p>"


def _start(lang):
    return f'<p><a class="btn btn--lg" href="{APP}/">{u("start", lang)}</a></p>'


def _safety(t, standing=False):
    s = f'<h2 id="safety">{t("Safety")}</h2>\n<p>{t("Stop if it hurts or you feel dizzy. Ask your doctor or therapist which exercises are right for you.")}</p>\n'
    s += f'<p>{t("Do not rely on the camera to keep you safe. It can miss a loss of balance.")} <a href="/safety">{t("What to know before you start")}</a></p>\n'
    return s


def _tags(t, e, lang):
    bits = [t("can be done seated") if e["seated"] else t("needs standing")]
    if e["free"]:
        bits.append(t("free plan"))
    return f' <small>({("、" if lang in CJK else ", ").join(bits)})</small>'


def _ex_li(t, e, lang):
    return f'<li><a href="/{move_slug(e)}">{e["name"][lang]}</a>{_sep(lang)}{e["instruction"][lang]}{_tags(t, e, lang)}</li>'


def _more(t, lang, extra=()):
    links = list(extra) + [("/practice", t("Practice library")), ("/faq", t("Frequently asked questions")), ("/safety", t("What to know before you start"))]
    return f'<p><strong>{t("More about Bonet")}</strong></p>\n<ul>' + "".join(f'<li><a href="{h}">{x}</a></li>' for h, x in links) + "</ul>"


def _note(t):
    return f'<p class="note">{t(DISCLAIMER[0])}</p>'


# ------------------------------------------------------------------ /practice/move/<slug>
def exercise_page(ctx, e, lang):
    t = _tools(lang)
    name, ins = e["name"][lang], e["instruction"][lang]
    area = AREA_BY_ID[e["areas"][0]]
    hold = e["hold"]
    title = _fit(t("{name}: home exercise counted by camera | Bonet", name=name), t("{name}: camera-counted exercise | Bonet", name=name), t("{name}: exercise | Bonet", name=name))
    plan = t("It is in the free plan.") if e["free"] else t("It is a Premium exercise.")
    desc = t("{name} in Bonet: {instruction} Your camera counts each repetition. {plan} Not a medical device.", name=name, instruction=ins, plan=plan)
    lede = (t("{name} is one of the {exercises} movement exercises in Bonet. A 3D guide shows the move, and your camera times each hold on your device. Bonet is a practice tool, not a medical device.", name=name) if hold
            else t("{name} is one of the {exercises} movement exercises in Bonet. A 3D guide shows the move, and your camera counts each repetition on your device. Bonet is a practice tool, not a medical device.", name=name))
    area_links = ", ".join(f'<a href="/{area_slug(AREA_BY_ID[a])}">{AREA_BY_ID[a]["title"][lang]}</a>' for a in e["areas"])
    glance = [t("Body area: {area}", area=area_links), t("Position: can be done seated") if e["seated"] else t("Position: needs standing")]
    if e["oneSided"]:
        glance.append(t("Sides: one side at a time"))
    glance += [t("Level in the app: {n} of 3", n=e["level"]), t("Tracking: the camera follows your hand") if e["mode"] == "hand" else t("Tracking: the camera follows your body"),
               t("Plan: included in the free plan") if e["free"] else t("Plan: Premium. The free plan includes {free_ex} of the {exercises} exercises.")]
    body = _trail(lang, [("/practice", t("Practice library")), ("/practice#move", t("Move")), (f"/{area_slug(area)}", area["title"][lang])])
    body += f'\n<h1>{name}</h1>\n<div class="alert"><p>{lede}</p></div>\n{_start(lang)}\n'
    body += f'<h2 id="glance">{t("At a glance")}</h2>\n<ul>' + "".join(f"<li>{x}</li>" for x in glance) + "</ul>\n"
    body += f'<h2 id="what">{t("What you do")}</h2>\n<p>{t("On the exercise screen, the app gives this instruction:")}</p>\n<blockquote><p>{ins}</p></blockquote>\n'
    steps = []
    if e["cues"] and e["id"] not in NO_CUES:
        steps = [e["cues"][k][lang] for k in ("progress", "hold", "relax")]
        body += f'<p>{t("While you move, short cues appear on the screen and are spoken aloud, in this order:")}</p>\n<ol>' + "".join(f"<li>{s}</li>" for s in steps) + "</ol>\n"
    body += f'<p>{t("You can switch the voice off in Settings. You can skip, shorten or repeat any exercise.")}</p>\n'
    body += f'<h2 id="count">{t("What the camera counts")}</h2>\n<p>{t(CAM[e["id"]])}</p>\n'
    if e["id"] not in NO_RULE:
        body += f'<p>{t(RULE[e["mode"]])}</p>\n'
    if e["leanCheck"]:
        body += f'<p>{t("When your hips are in the picture, the app also checks that your body stays upright. If you lean, it reminds you to keep your body straight and does not count until you do.")}</p>\n'
    body += ("<ul>" + f'<li>{t("The count is an estimate. Light, camera angle and loose clothing can change it.")}</li>' + f'<li>{t("Camera video is read on your device. It is never recorded or uploaded.")}</li>'
             + f'<li>{t("If the camera does not suit you, choose <q>{no_camera}</q> in the app and tap a button to count each repetition yourself.")}</li>' + "</ul>\n")
    body += f'<h2 id="setup">{t("How to set up your phone")}</h2>\n<p>{t("Put your phone, tablet or computer where the camera can see you.")} {t(VIEW[view_of(e)])}</p>\n'
    body += "<p>" + (t("This exercise can be done sitting in a stable chair.") if e["seated"] else t("This exercise needs you to stand. Stand next to a wall or a sturdy chair you can hold, and have someone nearby if balance is a concern."))
    body += " " + t("Use a clear space with good light. If the app cannot see you well enough, it stops counting until you are back in the picture.") + "</p>\n"
    body += _safety(t) + _start(lang) + "\n"
    peers = in_area(area)
    i = peers.index(e)
    rel = [peers[(i + k) % len(peers)] for k in range(1, 4)]
    body += f'<h2 id="related">{t("Related exercises")}</h2>\n<ul>' + "".join(_ex_li(t, r, lang) for r in rel) + "</ul>\n"
    body += _more(t, lang, [(f"/{area_slug(area)}", t("{area}: all exercises", area=area["title"][lang]))]) + "\n" + _note(t)
    ld = [_crumbs(lang, [("Bonet", "/"), (t("Practice library"), "/practice"), (area["title"][lang], f"/{area_slug(area)}"), (name, f"/{move_slug(e)}")])]
    if steps:  # steps are the app's own cue words, never written for this page
        ld.append({"@context": "https://schema.org", "@type": "HowTo", "name": name, "description": ins, "inLanguage": LANGS[lang]["tag"],
                   "step": [{"@type": "HowToStep", "position": n + 1, "text": s} for n, s in enumerate(steps)]})
    _write(ctx, lang, move_slug(e), title, desc, body, ld)


# ------------------------------------------------------------------ /practice/area/<slug>
def area_page(ctx, a, lang):
    t = _tools(lang)
    name = a["title"][lang]
    items = in_area(a)
    free = sum(e["free"] for e in items)
    title = _fit(t("{area}: home exercises counted by camera | Bonet", area=name), t("{area}: camera-counted exercises | Bonet", area=name))
    desc = t("{area}: the {n} exercises in Bonet, a home practice app. What each one asks you to do, which can be done seated and which are in the free plan. Not a medical device.", area=name, n=len(items))
    body = _trail(lang, [("/practice", t("Practice library")), ("/practice#move", t("Move"))])
    body += f'\n<h1>{t("{area}: {n} exercises to practise at home", area=name, n=len(items))}</h1>\n<div class="alert"><p>{t(AREA_INTRO[a["id"]])}</p></div>\n'
    body += f'<p>{t("A 3D guide shows each move, and your camera counts the repetitions on your device. {k} of these {n} exercises are in the free plan.", k=free, n=len(items))}</p>\n{_start(lang)}\n'
    body += f'<h2 id="list">{t("The exercises")}</h2>\n<ul>' + "".join(_ex_li(t, e, lang) for e in items) + "</ul>\n"
    body += f'<h2 id="setup">{t("How to set up your phone")}</h2>\n<p>{t("Put your phone, tablet or computer where the camera can see you.")} {t("Each exercise page says what the camera needs to see.")} '
    body += t("Use a clear space with good light. If the app cannot see you well enough, it stops counting until you are back in the picture.") + "</p>\n"
    body += "<ul>" + f'<li>{t("The count is an estimate. Light, camera angle and loose clothing can change it.")}</li>' + f'<li>{t("Camera video is read on your device. It is never recorded or uploaded.")}</li>' + "</ul>\n"
    body += _safety(t)
    body += f'<h2 id="areas">{t("Other body areas")}</h2>\n<ul>' + "".join(f'<li><a href="/{area_slug(o)}">{o["title"][lang]}</a></li>' for o in AREAS if o is not a) + "</ul>\n"
    body += _start(lang) + "\n" + _more(t, lang) + "\n" + _note(t)
    ld = [_crumbs(lang, [("Bonet", "/"), (t("Practice library"), "/practice"), (name, f"/{area_slug(a)}")]),
          {"@context": "https://schema.org", "@type": "ItemList", "name": name, "itemListElement": [
              {"@type": "ListItem", "position": n + 1, "name": e["name"][lang], "url": f"{parts.SITE}{pre(lang)}/{move_slug(e)}"} for n, e in enumerate(items)]}]
    _write(ctx, lang, area_slug(a), title, desc, body, ld)


# ------------------------------------------------------------------ /practice/speak/<slug>
def speak_page(ctx, m, lang):
    t = _tools(lang)
    name, purpose = m["name"][lang], m["purpose"][lang]
    c = SPEAK[m["id"]]
    n_modes, free = len(MODES), SPEECH["free_max_level"]
    title = _fit(t("{name}: " + c["tail"] + " | Bonet", name=name), t("{name}: speaking practice | Bonet", name=name))
    desc = (t("{name} in Bonet: {purpose} {levels} levels, hints that grow one step at a time, {langs} languages. A practice tool, not speech therapy.", name=name, purpose=purpose) if c["hints"]
            else t("{name} in Bonet: {purpose} {levels} levels in {langs} languages. A practice tool, not speech therapy.", name=name, purpose=purpose))
    body = _trail(lang, [("/practice", t("Practice library")), ("/practice#speak", t("Speak"))])
    body += f'\n<h1>{name}</h1>\n<div class="alert"><p>{t("{name} is one of the {n} kinds of speaking practice in Bonet. In the words of the app: <q>{purpose}</q> It has {levels} levels. Bonet is a practice tool, not speech therapy.", name=name, n=n_modes, purpose=purpose)}</p></div>\n{_start(lang)}\n'
    body += f'<h2 id="what">{t("What you do")}</h2>\n' + "".join(f"<p>{t(x)}</p>\n" for x in c["do"])
    body += f'<h2 id="hints">{t("How hints work")}</h2>\n'
    if c["hints"]:
        body += f'<p>{t("You get a hint. Hints grow one step at a time, so you get just enough help to keep going. Using hints is part of practice, not a mistake.")}</p>\n'
        body += f'<p>{t("You can ask for a hint, and after a miss the app offers the next one by itself. The steps in this practice, in order:")}</p>\n<ol>' + "".join(f"<li>{t(x)}</li>" for x in c["hints"]) + "</ol>\n"
    else:
        body += f'<p>{t("This practice has no hint steps. The cards are shown for a few seconds before each set so you can memorise them, and a wrong pair only turns back over. Nothing is taken away for a miss.")}</p>\n'
    body += f'<h2 id="levels">{t("Levels 1 to {levels}")}</h2>\n'
    body += f'<p>{t("Each type has {levels} levels, so you can begin where it feels comfortable and move up slowly. Items you found hard come back later for review.")}</p>\n'
    body += f'<p>{t("The levels are grouped in units of {unit}, and each level has its own everyday topic.", unit=SPEECH["unit"])}'
    if c["hints"]:  # cues.ts: the pass mark is taken on the items done at hint step 0 or 1
        body += " " + t("You pass a level with {pass} percent or more, and passing opens the next one. The percentage counts the items you did with no hint, or with only a repeat of the prompt.", **{"pass": SPEECH["pass_pct"]})
    body += f'</p>\n<p>{t("Levels 1 to {free} are in the free plan. Premium opens all {levels} levels.", free=free)}</p>\n'
    lead, items, tail = MEASURE[c["measure"]]
    body += f'<h2 id="measured">{t("What is measured")}</h2>\n' + "".join(f"<p>{t(x)}</p>\n" for x in lead)
    if items:
        body += "<ul>" + "".join(f"<li>{t(x)}</li>" for x in items) + "</ul>\n"
    body += "".join(f"<p>{t(x)}</p>\n" for x in tail)
    if c["measure"].startswith("spoken"):
        body += f'<p>{t(next(k for k in REUSE if k.startswith("Recognition runs")))}</p>\n'
    body += f'<h2 id="languages">{t("Languages")}</h2>\n<p>{t(LANG_LINE[0])} {t("Chinese comes as Cantonese, Traditional Chinese and Simplified Chinese. You practise in the language you choose for the app.")}</p>\n'
    body += f'<p>{t("Bonet is practice you do yourself. It does not assess your speech and does not replace a speech-language pathologist. Ask your therapist which practice suits you.")}</p>\n{_start(lang)}\n'
    body += f'<h2 id="related">{t("Other speaking practice")}</h2>\n<ul>' + "".join(f'<li><a href="/{speak_slug(o)}">{o["name"][lang]}</a>{_sep(lang)}{o["purpose"][lang]}</li>' for o in MODES if o is not m) + "</ul>\n"
    body += _more(t, lang, [("/speech-practice-at-home", u("f_speech", lang))]) + "\n" + _note(t)
    ld = [_crumbs(lang, [("Bonet", "/"), (t("Practice library"), "/practice"), (name, f"/{speak_slug(m)}")])]
    _write(ctx, lang, speak_slug(m), title, desc, body, ld)


# ------------------------------------------------------------------ /practice/think/<slug>
def _levels_table(t, g, lang):
    """What each level sets, from the app's own configuration and its own level labels."""
    gid = g["id"]
    lv = [PH[k][lang] for k in ("easy", "medium", "hard")]
    row = lambda a, b: f'<tr><th scope="row">{a}</th><td>{b}</td></tr>'
    if gid in ("span", "pairs", "trail"):
        rows = "".join(row(lv[n], PH[f"{gid}_{n + 1}"][lang]) for n in range(3))
        cfg = BRAIN[gid]
        extra = {"span": lambda: t("On harder levels the squares also light up faster, and the longest list grows from {a} to {b} squares.", a=cfg["1"]["maxSpan"], b=cfg["3"]["maxSpan"]),
                 "pairs": lambda: t("The time limit grows with the number of cards: {a}, {b} and {c} seconds.", a=cfg["1"]["timeLimitSec"], b=cfg["2"]["timeLimitSec"], c=cfg["3"]["timeLimitSec"]),
                 "trail": lambda: t("Each game has a few rounds, with the numbers in new places every round.")}[gid]()
        return f'<table><tbody>{rows}</tbody></table>\n<p>{extra}</p>\n'
    if gid == "math":
        cfg = BRAIN["math"]
        rows = "".join(row(lv[n], PH[f"math_{k}"][lang]) for n, k in enumerate(("simple", "medium", "hard")))
        extra = t("Harder levels also show more answers to choose from ({a}, {b} and {c}) and give less time for each question ({d}, {e} and {f} seconds).",
                  a=cfg["simple"]["choices"], b=cfg["medium"]["choices"], c=cfg["hard"]["choices"], d=cfg["simple"]["perRoundTime"], e=cfg["medium"]["perRoundTime"], f=cfg["hard"]["perRoundTime"])
        return f'<table><tbody>{rows}</tbody></table>\n<p>{extra}</p>\n'
    rows = row(lv[0], PH["few"][lang]) + row(lv[2], PH["more"][lang])
    rows2 = "".join(row(PH[f"level_{n}"][lang], PH[f"target_{n}"][lang]) for n in "123")
    return (f'<p>{t("When Bonet names one item, or when you keep going for a few minutes, there are two levels:")}</p>\n<table><tbody>{rows}</tbody></table>\n'
            f'<p>{t("When you pick every one of a kind, there are three levels:")}</p>\n<table><tbody>{rows2}</tbody></table>\n')


def think_page(ctx, g, lang):
    t = _tools(lang)
    name, what, grp = g["name"][lang], g["body"][lang], g["group"]
    c = THINK[g["id"]]
    title = _fit(t("{name}: " + GROUP_TAIL[grp["slug"]] + " | Bonet", name=name), t("{name}: brain game | Bonet", name=name))
    desc = t("{name}, a brain game in Bonet: {what} Several levels of difficulty, and the easiest is free. Not a medical device.", name=name, what=what)
    body = _trail(lang, [("/practice", t("Practice library")), ("/practice#think", t("Think"))])
    body += f'\n<h1>{name}</h1>\n<div class="alert"><p>{t("{name} is one of the {n} brain games in Bonet, in the group <q>{group}</q>. In the words of the app: <q>{what}</q> Bonet is a practice tool, not a medical device.", name=name, n=len(GAMES), group=grp["title"][lang], what=what)}</p></div>\n{_start(lang)}\n'
    body += f'<h2 id="what">{t("What you do")}</h2>\n' + "".join(f"<p>{t(x)}</p>\n" for x in c["do"]) + f'<p>{t(INPUT[c["input"]])}</p>\n'
    body += f'<h2 id="levels">{t("What the difficulty levels change")}</h2>\n' + _levels_table(t, g, lang)
    body += f'<p>{t("The easiest level is in the free plan. The other levels need Premium.")} {t("The app suggests a level from your own recent games, one step at a time. It is only a suggestion, and you choose.")}</p>\n'
    body += f'<h2 id="shown">{t("What the app shows afterwards")}</h2>\n<p>{t("After a game the app shows " + c["shown"] + ".")} {t("These numbers describe how one game went. The game is for practice. It is not a test of memory, attention or thinking.")}</p>\n{_start(lang)}\n'
    body += f'<h2 id="related">{t("Other brain games")}</h2>\n<ul>' + "".join(f'<li><a href="/{think_slug(o)}">{o["name"][lang]}</a>{_sep(lang)}{o["body"][lang]}</li>' for o in GAMES if o["id"] != g["id"]) + "</ul>\n"
    body += _more(t, lang) + "\n" + _note(t)
    ld = [_crumbs(lang, [("Bonet", "/"), (t("Practice library"), "/practice"), (name, f"/{think_slug(g)}")])]
    _write(ctx, lang, think_slug(g), title, desc, body, ld)


# ------------------------------------------------------------------ /practice
def hub(ctx, lang):
    t = _tools(lang)
    n_speak, n_think = len(MODES), len(GAMES)
    title = t("Practice library: exercises, speaking and brain games | Bonet")
    desc = t("Everything you can practise in Bonet: {exercises} camera-counted exercises by body area, {a} kinds of speaking practice and {b} brain games. Not a medical device.", a=n_speak, b=n_think)
    seated, standing, free = [e for e in EX if e["seated"]], [e for e in EX if not e["seated"]], [e for e in EX if e["free"]]
    names = lambda xs: ", ".join(f'<a href="/{move_slug(e)}">{e["name"][lang]}</a>' for e in xs)
    body = f'<h1>{t("Practice library")}</h1>\n<div class="alert"><p>{t("Everything you can practise in Bonet, listed from the app itself: {exercises} movement exercises, {a} kinds of speaking practice with {levels} levels each, and {b} brain games. Bonet is a practice tool, not a medical device.", a=n_speak, b=n_think)}</p></div>\n{_start(lang)}\n'
    body += (f'<div class="toc"><ul><li><a href="#move">{t("Move")}</a>{_sep(lang)}{t("{exercises} exercises counted by your camera")}</li><li><a href="#speak">{t("Speak")}</a>{_sep(lang)}{t("{a} kinds of speaking practice", a=n_speak)}</li>'
             f'<li><a href="#think">{t("Think")}</a>{_sep(lang)}{t("{b} brain games", b=n_think)}</li></ul></div>\n')
    body += f'<h2 id="move">{t("Move")}</h2>\n<p>{t("A 3D guide shows each move, and your camera counts the repetitions on your device. Choose by body area, or go straight to the exercises you can do seated.")}</p>\n'
    jump = [(f"#{a['slug']}", a["title"][lang]) for a in AREAS] + [("#seated", t("Can be done seated")), ("#standing", t("Needs standing")), ("#free", t("In the free plan"))]
    body += f'<p><strong>{t("Jump to")}</strong> ' + " | ".join(f'<a href="{h}">{x}</a>' for h, x in jump) + "</p>\n"
    body += (f'<figure><div class="card-demo" data-ss-fill><div class="demo" data-demo="move" role="img" aria-label="{parts.esc(t(DEMO_ALT["move"][0]))}"></div></div></figure>\n')
    for a in AREAS:
        items = in_area(a)
        body += f'<h3 id="{a["slug"]}"><a href="/{area_slug(a)}">{a["title"][lang]}</a></h3>\n<ul>' + "".join(_ex_li(t, e, lang) for e in items) + "</ul>\n"
    body += f'<h3 id="seated">{t("Can be done seated")}</h3>\n<p>{names(seated)}</p>\n<h3 id="standing">{t("Needs standing")}</h3>\n<p>{names(standing)}</p>\n<h3 id="free">{t("In the free plan")}</h3>\n<p>{names(free)}</p>\n'
    body += f'<p>{t("Stop if it hurts or you feel dizzy. Ask your doctor or therapist which exercises are right for you.")}</p>\n'
    body += f'<h2 id="speak">{t("Speak")}</h2>\n<p>{t("Each kind of speaking practice has {levels} levels. Levels 1 to {free} are in the free plan.", free=SPEECH["free_max_level"])}</p>\n<ul>'
    body += "".join(f'<li><a href="/{speak_slug(m)}">{m["name"][lang]}</a>{_sep(lang)}{m["purpose"][lang]}</li>' for m in MODES) + "</ul>\n"
    body += f'<h2 id="think">{t("Think")}</h2>\n<p>{t("Short games in {n} groups. The easiest level of every game is in the free plan.", n=len(BRAIN["groups"]))}</p>\n'
    for grp in BRAIN["groups"]:
        body += f'<h3 id="{grp["slug"]}">{grp["title"][lang]}</h3>\n<ul>' + "".join(f'<li><a href="/{think_slug(g)}">{g["name"][lang]}</a>{_sep(lang)}{g["body"][lang]}</li>' for g in grp["games"]) + "</ul>\n"
    need = [(f"/{p}", u(parts.NEED_UI[p], lang)) for p in parts.NEED_PAGES]
    links = need + [("/faq", t("Frequently asked questions")), ("/safety", t("What to know before you start"))]
    body += _start(lang) + f'\n<p><strong>{t("More about Bonet")}</strong></p>\n<ul>' + "".join(f'<li><a href="{h}">{x}</a></li>' for h, x in links) + "</ul>\n" + _note(t)
    ld = [_crumbs(lang, [("Bonet", "/"), (t("Practice library"), "/practice")])]
    _write(ctx, lang, "practice", title, desc, body, ld, demos=True)


def llms_section():
    """Lines for /llms.txt: the hub and the body-area pages (English)."""
    L = lambda path, name, note: f"- [{name}]({parts.SITE}{path}): {note}"
    out = [L("/practice", "Practice library", f"Every exercise ({len(EX)}), kind of speaking practice ({len(MODES)}) and brain game ({len(GAMES)}) in the app, each with its own page under /practice/move/, /practice/speak/ and /practice/think/.")]
    for a in AREAS:
        items = in_area(a)
        out.append(L(f"/{area_slug(a)}", f"{a['title']['en']} exercises", f"{len(items)} exercises: " + ", ".join(e["name"]["en"] for e in items) + "."))
    return "\n".join(out)


def build(ctx):
    for lang in LANGS:
        hub(ctx, lang)
        for a in AREAS:
            area_page(ctx, a, lang)
        for e in EX:
            exercise_page(ctx, e, lang)
        for m in MODES:
            speak_page(ctx, m, lang)
        for g in GAMES:
            think_page(ctx, g, lang)


if __name__ == "__main__":  # the strings a translator needs: every English string these pages ask for
    class _Null:
        head, header, footer = staticmethod(parts.head), staticmethod(parts.header), staticmethod(parts.footer)
        write = staticmethod(lambda rel, text: None)
    lang = "en"
    hub(_Null, lang)
    [area_page(_Null, a, lang) for a in AREAS]
    [exercise_page(_Null, e, lang) for e in EX]
    [speak_page(_Null, m, lang) for m in MODES]
    [think_page(_Null, g, lang) for g in GAMES]
    print(json.dumps(USED, ensure_ascii=False, indent=1))
