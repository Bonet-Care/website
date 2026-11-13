"""The home page, English and Cantonese. Copy sits next to its translation: T("English", "廣東話")."""
import json
import re
import parts
from cost import cost_section
from parts import NUM_WORD, NUM_YUE, LANG_COUNT, APP, MAIL, SITE, esc, footer, head, header, mk, price_html, price_text, LANGS, PRICES

ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent
CMP = json.loads((ROOT / "scripts" / "competitors.json").read_text())
PQ = json.loads((ROOT / "content" / "practice-quality.json").read_text())  # requires_feature: practice_quality
ROWS_ORDER = None

# Cantonese for the short notes in the comparison table (keyed by the English note).
ZHN = {
    "Pages cover speech, language, cognition only": "頁面只講說話、語言同認知",
    "Listed apps are language, speech, cognition, swallowing": "列出嘅 app 係語言、說話、認知同吞嚥",
    "Page lists language and cognitive exercises only": "頁面只列語言同認知練習",
    "FitMi counts reps with sensor pucks, no camera": "FitMi 用感應器圓盤數次數，冇用鏡頭",
    "Shows exercises; nothing counts reps or checks form": "只係示範動作，冇人數次數或者睇姿勢",
    "Speech exercises listed beside language and cognition": "說話練習同語言、認知練習放埋一齊",
    "Separate apraxia and conversation apps; scoring of speech unverified": "有分開嘅失用症同對話 app；有冇為說話評分未核實",
    "Speaking tasks; iPad playback of own recording, self-review": "有說話練習；喺 iPad 播返自己錄音自行檢視",
    "CT app lists speech exercises; voice scoring not described": "CT app 列有說話練習；冇講明有冇語音評分",
    "Can list speech exercises; no feedback or hints": "可以列出說話練習；冇回饋或者提示",
    "Cognitive skills exercises, adaptive difficulty": "認知練習，難度會調整",
    "Few cognition apps, e.g. visual attention, spaced retrieval": "有少量認知 app，例如視覺專注、間隔回想",
    "Over 13,500 language and cognitive exercises": "超過 13,500 個語言同認知練習",
    "CT app covers attention, memory and math": "CT app 有專注、記憶同數學",
    "Paper puzzles or worksheets possible; no adaptation": "可以用紙本遊戲或者工作紙；難度唔會調整",
    "Homework plan in Tasks tab; speech and cognition only": "「任務」入面有功課計劃；只有說話同認知",
    "Separate paid apps; no combined plan described": "分開買嘅 app；冇講明有合併計劃",
    "Page silent on plans; app store listing not readable": "頁面冇提計劃；應用商店頁面讀唔到",
    "Devices and CT app sold separately; no joint plan described": "裝置同 CT app 分開賣；冇講明有共用計劃",
    "A written weekly sheet can combine all three": "一張每週紙可以包埋三樣",
    "Product page and FAQ mention no streaks or rewards": "產品頁同常見問題冇提連續練習或獎勵",
    "Page describes no streaks, leagues or rewards": "頁面冇講連續練習、聯賽或獎勵",
    "Page mentions no game elements": "頁面冇提遊戲元素",
    "MusicGlove is a music game; no streaks or leagues described": "MusicGlove 係音樂遊戲；冇講連續練習或聯賽",
    "None": "冇",
    "Reports tab, emailed reports, therapist can be linked": "有報告版面、電郵報告，可以連結治療師",
    "Apps create automatic reports; clinician dashboard not described": "app 會自動做報告；冇講明有臨床儀表板",
    "Page silent on reports; app store listing not readable": "頁面冇提報告；應用商店頁面讀唔到",
    "CT app reports, clinician can be added; FitMi sharing not stated": "CT app 有報告，可以加入臨床人員；FitMi 有冇分享冇講明",
    "Paper log kept by hand at best": "最多係手寫紀錄",
    "English and Spanish; no Chinese found": "英文同西班牙文；搵唔到中文",
    "English, Spanish, French, German; no Chinese found": "英文、西班牙文、法文、德文；搵唔到中文",
    "Site in English and Spanish; exercise languages not stated": "網站有英文同西班牙文；練習語言冇講明",
    "Product pages state no languages": "產品頁冇講語言",
    "Any language the author writes it in": "作者用咩語言寫都得",
    "Browser, iOS, Android, Chromebook, Kindle Fire": "瀏覽器、iOS、Android、Chromebook、Kindle Fire",
    "iOS and Android apps; browser version not mentioned": "iOS 同 Android app；冇提瀏覽器版本",
    "Web and iPad app; Android not mentioned": "網頁同 iPad app；冇提 Android",
    "FitMi needs Mac/PC with USB or Flint tablet; CT app on phones and web": "FitMi 要用 Mac/PC 接 USB 或者 Flint 平板；CT app 有手機同網頁版",
    "Paper, or any screen that plays video": "紙本，或者任何播得影片嘅螢幕",
    "$29.99 per month; first two weeks free; currency not named": "每月 $29.99；頭兩星期免費；冇講貨幣",
    "One-time US$89.99 Language 4-in-1; free Lite apps; no subscription": "一次性 US$89.99（Language 4-in-1）；有免費 Lite app；冇訂閱",
    "Free account and exercises": "免費帳戶同練習",
    "CT app $29.99/month; FitMi $399; currency not named": "CT app 每月 $29.99；FitMi $399；冇講貨幣",
    "Often free from a clinic; printing cost only": "通常診所免費提供；最多係印刷費",
}
QZH = {}
ZHV = {"yes": "有", "no": "冇", "partly": "部分", "not offered as far as we can tell": "據我哋所知冇提供", "unverified": "未核實"}
ENV = {"yes": "Yes", "no": "No", "partly": "Partly", "not offered as far as we can tell": "Not offered, as far as we can tell", "unverified": "Not checked"}
ZHLAB = {
    "movement": "鏡頭數次數嘅運動練習", "speaking": "說話練習", "cognitive": "腦力遊戲或認知練習", "dailyPlan": "運動、說話、腦力共用一個每日計劃",
    "gameElements": "遊戲元素（連續練習、聯賽、吉祥物）", "report": "可以俾治療師或家人睇嘅報告", "languages": "語言",
    "platforms": "喺邊度用得", "price": "開始時嘅價錢（頁面標價，2026 年 11 月）",
}
ENLAB = {"movement": "Movement practice, with a camera counting reps", "speaking": "Speaking practice", "cognitive": "Brain games or cognitive exercises",
         "dailyPlan": "One daily plan across movement, speaking and brain practice", "gameElements": "Game elements (streak, league, mascot)",
         "report": "A report to share with a therapist or family", "languages": "Languages", "platforms": "Where it runs",
         "price": "Price to start (published, November 2026)"}
BONET = {
    "movement": (("yes", "The camera counts reps on your device, with tips"), ("yes", "鏡頭喺你部機數次數，仲有小提示")),
    "speaking": (("yes", "Hint ladder, words heard, pace and pauses"), ("yes", "有提示階梯，會顯示聽到嘅詞語、速度同停頓")),
    "cognitive": (("yes", "Short memory and attention games"), ("yes", "簡短嘅記憶同專注遊戲")),
    "dailyPlan": (("yes", "One daily path with all three"), ("yes", "一條每日路徑包埋三樣")),
    "gameElements": (("yes", "Streak with savers, weekly league, corgi outfits"), ("yes", "有保護盾嘅連續練習、每週聯賽、柯基衣服")),
    "report": (("partly", "One-page report you share yourself; no clinician dashboard"), ("partly", "一頁報告，由你自己分享；冇臨床儀表板")),
    "languages": (("yes", f"{NUM_WORD[LANG_COUNT]} languages"), ("yes", f"{NUM_YUE[LANG_COUNT]}種語言")),
    "platforms": (("partly", "Browser today; iPhone and iPad app coming soon"), ("partly", "而家用瀏覽器；iPhone 同 iPad 版本即將推出")),
    "price": (("yes", "Free to start; Premium HK$78 a month, 7 days free"), ("yes", "免費開始；完整版每月 HK$78，免費試用 7 日")),
}
BETTER = {
    0: ("Constant Therapy reports a company-run Phase II trial of its app in post-stroke aphasia, holds an FDA Breakthrough Device designation (priority review, not authorisation) and has a separate Clinician App.",
        "Constant Therapy 報告過一個公司自己進行嘅中風後失語症第二期試驗，持有 FDA 突破性器材認定（係優先審查，並非批准），亦有獨立嘅臨床人員 app。"),
    1: ("Tactus Therapy has 19 single-purpose apps made by a certified speech-language pathologist, with a cueing hierarchy, bought once.",
        "Tactus Therapy 有 19 個單一用途 app，由認可言語治療師製作，有提示層級，一次買斷。"),
    2: ("TalkPath is free and lists more than 13,500 exercises, far more than Bonet has.", "TalkPath 免費，列有超過 13,500 個練習，遠多過哥基健動。"),
    3: ("Flint Rehab sells an FDA-listed device with four published studies, and a remote programme where a licensed therapist builds the plan.",
        "Flint Rehab 有 FDA 登記嘅裝置同四項已發表研究，亦有由持牌治療師訂立計劃嘅遠程課程。"),
}


def dedupe_sources():
    seen, out = set(), []
    for r in CMP["rows"]:
        for c, v in r["cells"].items():
            u = v.get("src")
            if u and u.startswith("http") and u not in seen:
                seen.add(u)
                out.append((c, u))
    return out



SHORT = {  # one or two words per row for the home page table; marks for the rest
    "movement": "Camera counts reps", "speaking": "Speaking practice", "cognitive": "Brain games", "dailyPlan": "One daily plan",
    "gameElements": "Streak, league, mascot", "quality": "Practice tips", "languages": "Languages",
}
SHORT_ZH = {"Camera counts reps": "鏡頭數次數", "Speaking practice": "說話練習", "Brain games": "腦力遊戲", "One daily plan": "一個每日計劃", "Streak, league, mascot": "連續練習、聯賽、吉祥物", "Practice tips": "練習提示", "Languages": "語言"}
MARK = {"yes": ("\u2713", "Yes"), "no": ("\u2013", "No"), "not offered as far as we can tell": ("\u2013", "Not offered, as far as we can tell"), "partly": ("Part", "Partly"), "unverified": ("?", "Not checked")}
SHORT_NOTE = {("Constant Therapy", "speaking"): "", ("Flint Rehab", "movement"): "Sensors"}


def compare(lang):
    """Short table for the home page: marks, no sentences. Details and sources live on /compare.html."""
    t = mk(lang)
    cols = ["Constant Therapy", "Tactus Therapy", "Exercise video or paper handout"]
    keys = ["movement", "speaking", "cognitive", "dailyPlan", "gameElements", "languages"]
    if "practice_quality" not in parts.FLAGS_OFF:
        keys.insert(5, "quality")
    by_key = {r["key"]: r for r in CMP["rows"]}
    th = "".join(f'<th scope="col">{c if c != "Exercise video or paper handout" else t("Paper handout", "紙本講義")}</th>' for c in cols)
    rows = ""
    for k in keys:
        lab = t(SHORT[k], SHORT_ZH[SHORT[k]])
        cells = f'<td class="us"><span class="mk y" aria-label="{t("Yes", "有")}">{str(LANG_COUNT) if k == "languages" else chr(10003)}</span></td>'
        for c in cols:
            if k == "quality":
                v = PQ["row_cells"][c][0]
            else:
                v = by_key[k]["cells"][c]["v"]
            mark, name = MARK[v]
            full = t(ENV[v], ZHV[v])
            cls = "y" if v == "yes" else "p" if v == "partly" else "n"
            txt = t("Part", "部分") if v == "partly" else mark
            if k == "languages":
                txt = {"Constant Therapy": "2", "Tactus Therapy": "4"}.get(c, "1+"); cls = "p"; full = txt
            cells += f'<td><span class="mk {cls}" aria-label="{full}">{txt}</span></td>'
        rows += f'<tr><th scope="row">{lab}</th>{cells}</tr>'
    legend = t("\u2713 yes, Part = partly, \u2013 not offered as far as we can tell.", "\u2713 有，部分 = 部分有，\u2013 據我哋所知冇提供。")
    return f"""<div class="cmpwrap" role="region" tabindex="0" aria-label="{t('Comparison table', '比較表')}"><table class="cmp cmp--s"><thead><tr><th scope="col"><span class="sr">{t('Feature', '項目')}</span></th><th scope="col" class="us">Bonet</th>{th}</tr></thead><tbody>{rows}</tbody></table></div>
<p class="asof">{legend} {t('As of November 2026.', '資料截至 2026 年 11 月。')} <a href="/compare.html">{t('Notes and sources', '附註同來源')}</a></p>"""

def compare_full(lang):
    t = mk(lang)
    cols = CMP["columns"]
    th = "".join(f'<th scope="col">{c if c != "Exercise video or paper handout" else t("Exercise video or paper handout", "運動影片或紙本講義")}</th>' for c in cols)
    rows = ""
    all_rows = list(CMP["rows"])
    if "practice_quality" not in parts.FLAGS_OFF:
        q = {"key": "quality", "cells": {c: {"v": v[0], "note": v[1]} for c, v in PQ["row_cells"].items()}}
        QZH.update({v[1]: v[2] for v in PQ["row_cells"].values()})
        all_rows.insert(4, q)
    for r in all_rows:
        k = r["key"]
        if k == "quality":
            lab = t(PQ["row_label"][0], PQ["row_label"][1]); bv = "yes"; bn = t(PQ["row_bonet"][0], PQ["row_bonet"][1])
        else:
            lab = t(ENLAB[k], ZHLAB[k]); bv = BONET[k][0][0]; bn = t(BONET[k][0][1], BONET[k][1][1])
        cells = f'<td class="us"><span class="v">{t(ENV[bv], ZHV[bv])}</span><span class="s">{bn}</span></td>'
        for c in cols:
            cell = r["cells"][c]
            v = cell["v"]
            cls = "no" if v in ("no", "not offered as far as we can tell") else "un" if v == "unverified" else ""
            note = cell["note"]
            note = t(note, ZHN.get(note) or QZH.get(note, note))
            cells += f'<td><span class="v {cls}">{t(ENV[v], ZHV[v])}</span><span class="s">{note}</span></td>'
        rows += f"<tr><th scope=\"row\">{lab}</th>{cells}</tr>"
    better = "".join(f"<li>{t(BETTER[i][0], BETTER[i][1])}</li>" for i in range(4))
    srcs = "".join(f'<li>{n}: <a href="{u}">{u}</a></li>' for n, u in dedupe_sources()[:14])
    asof = t("As of November 2026, from each vendor's own public pages. Where a page did not say, we wrote \"not offered as far as we can tell\" or \"not checked\" instead of guessing. Names are in plain text; we are not connected to any of these companies.", "資料截至 2026 年 11 月，來自各公司自己嘅公開頁面。頁面冇講明嘅地方，我哋寫「據我哋所知冇提供」或者「未核實」，唔會估。公司名稱只係文字，我哋同呢啲公司冇任何關係。")
    asof2 = t("Bonet has not been tested in a clinical trial and is not a medical device. How long each company has been in the market was not stated on the pages we read, so we make no claim about it.", "哥基健動未經臨床試驗，亦唔係醫療器材。各公司入市幾耐，我哋睇過嘅頁面冇講明，所以唔作比較。")
    return f"""<div class="cmpwrap" role="region" tabindex="0" aria-label="{t('Comparison table, scrolls sideways on small screens', '比較表，細螢幕可以左右捲動')}"><table class="cmp"><thead><tr><th scope="col"><span class="sr">{t('Feature', '項目')}</span></th><th scope="col" class="us">Bonet</th>{th}</tr></thead><tbody>{rows}</tbody></table></div>
<p class="asof">{asof}</p>
<div class="better"><h3>{t('What others do better', '其他產品做得更好嘅地方')}</h3><ul>{better}</ul>
<p class="asof">{asof2}</p></div>
<details class="srcd"><summary>{t('Sources for the table', '表格資料來源')}</summary><ul class="srcs">{srcs}</ul></details>"""


def faq_items(lang):
    """Four short answers for the home page; the full set is on /faq. Each ends with a link there."""
    t = mk(lang)
    pre = "" if LANGS[lang]["path"] == "/" else LANGS[lang]["path"].rstrip("/")
    more = f' <a href="{pre}/faq">{t("More answers", "更多答案")}</a>'
    return [
        (t("Is Bonet a medical device or a therapy?", "哥基健動係醫療器材或者治療嗎？"),
         t("No. Bonet is a practice tool for home. It does not diagnose or treat anything.", "唔係。哥基健動係喺屋企用嘅練習工具，唔會診斷或者治療任何嘢。") + more),
        (t("Does my camera video get uploaded?", "我嘅鏡頭影像會唔會被上載？"),
         t("No. Video is processed on your device and is never uploaded or recorded.", "唔會。影像只喺你部機處理，唔會上載或者錄低。") + more),
        (t("Which languages does it speak?", "支援邊幾種語言？"),
         t(f"{NUM_WORD[LANG_COUNT]} languages: English, Chinese, Japanese, Spanish, German and French.", f"{NUM_YUE[LANG_COUNT]}種語言：英文、中文、日文、西班牙文、德文同法文。") + more),
        (t("What is free, and what is Premium?", "免費同完整版有咩分別？"),
         t("Free covers the basics. Premium is {price} a month, with 7 days free.", "免費版有基本功能。完整版每月 {price}，可免費試用 7 日。") + more),
    ]


def video_for(lang):
    """Per-language demo video, decided at build time from the files present (no 404s); falls back to English."""
    d = ROOT / "media" / "demo"
    code = lang
    if not (d / f"bonet-demo-{code}.mp4").exists():
        code = "en"
    poster = f"bonet-demo-{code}.jpg" if (d / f"bonet-demo-{code}.jpg").exists() else "bonet-demo-en.jpg"
    vtt = f' data-vtt="/media/demo/bonet-demo-{code}.vtt"' if (d / f"bonet-demo-{code}.vtt").exists() else ""
    return {"src": f"/media/demo/bonet-demo-{code}.mp4", "poster": f"/media/demo/{poster}", "vtt": vtt}


def home(lang):
    T = mk(lang)
    base = LANGS[lang]["path"]
    title = T("Bonet: daily home practice for movement, speaking and brain games", "哥基健動 Bonet：喺屋企每日練習運動、說話同腦力")
    desc = T("A daily practice app for older adults. Move with your camera counting reps, practise speaking with hints, and play short brain games, with a corgi coach named Bonet. Free to start. A practice tool, not a medical device.",
             "為長者而設嘅每日練習：鏡頭幫你數運動次數、有提示嘅說話練習、簡短腦力遊戲，仲有柯基教練朱古力陪你。免費開始。呢個係練習工具，唔係醫療器材。")
    ld = [
        {"@context": "https://schema.org", "@type": "Organization", "@id": SITE + "/#organization", "name": "Coglix Labs Inc.", "url": SITE + "/", "logo": SITE + "/icon-512.png", "email": MAIL},
        {"@context": "https://schema.org", "@type": "SoftwareApplication", "@id": SITE + "/#software", "name": "Bonet", "alternateName": "哥基健動", "url": SITE + "/",
         "image": SITE + "/img/" + ("og-en.png" if lang == "en" else "og-zh.png"), "applicationCategory": "LifestyleApplication", "operatingSystem": "Web browser",
         "inLanguage": [x["tag"] for x in LANGS.values()], "description": desc, "publisher": {"@id": SITE + "/#organization"}, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).replace("{price}", price_text(lang))}} for q, a in faq_items(lang)]},
    ]
    extra = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
    h = head(lang, title, desc, SITE + base, "og-en.png" if lang == "en" else "og-zh.png", extra=extra, alt={c: SITE + d["path"] for c, d in LANGS.items()})
    h += header(lang)
    price = price_text(lang)
    vid = video_for(lang)
    vnote = f'<p class="vnote">{T("Video in English", "影片係英文")}</p>' if lang != "en" and vid["src"].endswith("-en.mp4") else ""

    pq_on = "practice_quality" not in parts.FLAGS_OFF

    def demo(name, label):
        extra = ' data-pq="1"' if (name == "hero" and pq_on) else ""
        return f'<div class="demo" data-demo="{name}"{extra} role="img" aria-label="{esc(label)}"></div>'

    def card(name, label, cls=""):
        return f'<div class="card-demo rv-tilt {cls}" data-ss-fill>{demo(name, label)}</div>'

    def word(w, icon, cls=""):
        return f'<h2 class="display {cls} rv-word">{w}</h2>'

    def pts(*xs):
        return '<ul class="pts">' + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"

    segs = T("A little practice,|every day.", "每日練習一啲，|輕輕鬆鬆。").split("|")
    h1 = ""; n = 0
    for si, seg in enumerate(segs):
        for w in ([seg] if " " not in seg else seg.split(" ")):
            h1 += f'<span class="w{" b" if si else ""}" style="--i:{n}">{w}</span> '; n += 1
    faq = "".join(f"<details><summary>{q}</summary><div><p>{a.replace('{price}', price)}</p></div></details>" for q, a in faq_items(lang))
    free = [T("Speaking levels 1 to 3", "說話第 1 至 3 級"), T("Eight starter exercises", "八個入門運動"), T("Easy brain games", "簡單腦力遊戲")]
    prem = [T("Every level and exercise", "全部級別同運動"), T("Harder brain games", "較難嘅腦力遊戲"), T("Longer reports", "更長嘅報告")]
    li = lambda xs: "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
    hk = "" if (PRICES.get("checkout_matches") or lang == "yue") else " " + T("For now, checkout charges Hong Kong dollars (HK$78).", "暫時以港元（HK$78）收費。")
    pq = ""
    if "practice_quality" not in parts.FLAGS_OFF:
        P = lambda k: T(PQ[k][0], PQ[k][1])
        pq = f"""<!-- requires_feature: practice_quality -->
<section class="sec sec--wash" id="quality"><div class="wrap">
<div class="open">{word(P('h2'), 'chart')}<p class="kicker rv">{P('kicker')}</p></div>
<div class="duo">
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('qmove', T('Animated preview: after a set, a six-sided chart draws itself and moves from last time to today, then a tip card slides in.', '動畫預覽：做完一組，六角形圖表逐邊畫出，由上次變成今次，跟住出現提示卡。'))}</div><div class="tcap"><h3>{P('move_h')}</h3></div></div>
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('qspeak', T('Animated preview: after speaking practice, a six-sided chart of words heard, pace and pauses moves from last time to today.', '動畫預覽：說話練習之後，聽到嘅詞語、速度同停頓六角形圖表由上次變成今次。'))}</div><div class="tcap"><h3>{P('speak_h')}</h3></div></div>
</div>
<p class="note" style="margin-top:2rem">{P('caveat')}</p>
</div></section>
<!-- /requires_feature -->
"""
    body = f"""<main id="main">
<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<h1>{h1}</h1>
<div class="cta-row"><a class="btn btn--lg" href="{APP}/">{T('Start free', '免費開始')}</a><a class="btn btn--2 btn--lg" href="#how">{T('See how it works', '睇下點用')}</a></div>
</div>
<div class="hero-art" data-ss-fill>
<span class="fl" style="left:4%;top:8%;width:3.2rem;--k:18" data-par><img src="/img/icons/star.webp" width="128" height="128" alt=""></span>
<div class="corgi" data-corgi role="img" aria-label="{T('Bonet the corgi', '朱古力')}"><button type="button" class="pupbtn" data-hover="wiggle" tabindex="-1" aria-hidden="true"><span class="sprite" data-clip="wave" data-then="idle" data-loops="2" data-rest="idle"></span></button></div>
{demo('hero', T('Animated preview: tap Start on the Today path, the camera counts three arm raises, Great set, and the step is ticked.', '動畫預覽：喺「今日」路徑撳開始，鏡頭數三下舉手，完成一組，然後打咗剔。'))}
</div></div></section>

<section class="sec sec--wash" id="how"><div class="wrap">
<div class="feat">
<div class="feat-copy">{word(T('Move', '運動'), 'muscle')}
<p class="kicker rv">{T('The camera counts your reps.', '鏡頭幫你數次數。')}</p></div>
<div class="feat-art">{card('move', T('Animated preview of the exercise screen counting 1, 2, 3 reps beside a 3D guide.', '動畫預覽：運動畫面一邊有立體示範，一邊數 1、2、3 下。'))}</div>
</div>

<div class="feat feat--flip">
<div class="feat-copy">{word(T('Speak', '說話'), 'speak')}
<p class="kicker rv">{T('Hints start small and grow, one step at a time.', '提示由細開始，一步一步加大。')}</p>
<div class="card-demo rv-tilt" style="max-width:420px;margin-top:.6rem">{demo('hint', T('Animated preview: tapping Give me a hint shows three hints, one after another.', '動畫預覽：撳「俾啲提示」，三個提示逐個出現。'))}</div></div>
<div class="feat-art">{card('speak', T('Animated preview: word tiles move into place to build a sentence and Great! appears.', '動畫預覽：詞語磚砌成句子，然後出現「好呀！」。'))}</div>
</div>

<div class="feat">
<div class="feat-copy">{word(T('Think', '腦力'), 'brain', 'display--or')}
<p class="kicker rv">{T('Short games for memory and attention.', '訓練記憶同專注嘅短遊戲。')}</p></div>
<div class="feat-art">{card('brain', T('Animated preview: two cards flip and match in a pairs game.', '動畫預覽：配對遊戲入面兩張牌翻開並且配成一對。'))}</div>
</div>
</div></section>

{pq}
<section class="sec"><div class="wrap">
<div class="open">{word(T('Also on a big screen', '大螢幕都用得'), 'globe', 'display--ink')}</div>
<div class="card-demo rv-tilt card-demo--wide" data-ss-fill>{demo('web', T('Animated preview of Bonet in a browser: the Move tab, an exercise started, and three reps counted.', '動畫預覽：喺瀏覽器用哥基健動，打開運動版、開始一個運動、數咗三下。'))}</div>
</div></section>

<section class="sec sec--blue"><div class="wrap">
<div class="open">{word(T('Big. Calm. Easy.', '大字。清晰。簡單。'), 'sun')}</div>
<div class="duo">
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('simple', T('Animated preview: turning on Simple mode changes a busy list into one big Start button.', '動畫預覽：開啟簡單模式，一堆選項變成一個大大嘅開始掣。'))}</div><div class="tcap"><h3>{T('Simple mode', '簡單模式')}</h3></div></div>
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('lang', T(f'Animated preview: a greeting changes through {NUM_WORD[LANG_COUNT].lower()} languages.', f'動畫預覽：問候語轉換{NUM_YUE[LANG_COUNT]}種語言。'))}</div><div class="tcap"><h3>{T(f'{NUM_WORD[LANG_COUNT]} languages', f'{NUM_YUE[LANG_COUNT]}種語言')}</h3></div></div>
</div></div></section>

<section class="sec"><div class="wrap">
<div class="open">{word(T('Come back tomorrow.', '聽日再嚟。'), 'fire', 'display--ink')}</div>
<div class="trio">
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('streak', T('Animated preview: a streak calendar where a saver covers a missed day.', '動畫預覽：連續練習日曆，保護盾補返漏咗嗰日。'))}</div><div class="tcap"><h3>{T('Keep your streak', '保持連續練習')}</h3></div></div>
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('league', T('Animated preview: a weekly league where your row climbs after practice.', '動畫預覽：每週聯賽，練習後你嘅名次上升。'))}</div><div class="tcap"><h3>{T('Weekly league', '每週聯賽')}</h3></div></div>
<div class="rv-tilt"><div class="card-demo" data-ss-fill data-wardrobe>{demo('wardrobe', T('Animated preview: Bonet the corgi trying on a bandana, a bow tie, a cap and a crown.', '動畫預覽：朱古力試戴頸巾、領結、棒球帽同小皇冠。'))}</div><div class="tcap"><h3>{T('Dress up Bonet', '幫朱古力換衫')}</h3></div></div>
</div></div></section>

<section class="sec sec--wash"><div class="wrap">
<div class="feat">
<div class="feat-copy"><h2 class="display rv-word">{T('Progress you can see.', '睇得到嘅進度。')}</h2>
<p class="kicker rv">{T('Share a one-page report with your therapist or family.', '一頁報告，可以俾治療師或者家人睇。')}</p></div>
<div class="feat-art"><div class="card-demo rv-tilt" data-ss-fill>{demo('progress', T('Animated preview: a weekly progress chart drawing in.', '動畫預覽：每週進度圖表逐條畫出。'))}</div>
<div class="paper rv" aria-hidden="true"><img src="/img/mascot/point.webp" width="512" height="512" alt=""><h4>{T('Home practice report', '居家練習報告')}</h4><small>{T('Last 2 weeks', '最近 2 星期')}</small>
<div class="bars rv-bars">{''.join(f'<i style="height:{x}%;--i:{n}"></i>' for n, x in enumerate([45, 70, 30, 85, 60, 95, 75]))}</div><div class="ln"></div><div class="ln m"></div><div class="ln s"></div></div></div>
</div></div></section>

<section class="sec" id="compare"><div class="wrap">
<div class="open"><h2 class="display display--ink rv-word">{T('How Bonet compares', '同其他方案比較')}</h2></div>
{compare(lang)}
</div></section>

<section class="wrap"><div class="strip"><p class="rv">{T('Camera video stays on your device. <span>Bonet is not a medical device.</span>', '鏡頭影像只留喺你部機。<span>哥基健動唔係醫療器材。</span>')}</p>
<a class="btn btn--2" href="/compliance.html">{T('Privacy and safety', '私隱與安全')}</a></div></section>

<section class="sec sec--wash"><div class="wrap">
<div class="open"><h2 class="rv">{T('Bonet in 50 seconds', '五十秒睇晒哥基健動')}</h2></div>
<button type="button" class="player rv-tilt" data-video="{vid["src"]}"{vid["vtt"]} data-lang="{LANGS[lang]["name"]}" aria-label="{T('Play the demo video', '播放示範影片')}"><img src="{vid["poster"]}" width="1280" height="720" alt="" loading="lazy"><span class="play" aria-hidden="true"></span></button>
<noscript><p class="vnote"><a href="{vid["src"]}">{T('Open the demo video', '開啟示範影片')}</a></p></noscript>
{vnote}
</div></section>

{cost_section(lang)}
<section class="sec" id="plans"><div class="wrap">
<div class="open"><h2 class="display display--ink rv-word">{T('Start free.', '免費開始。')}</h2></div>
<div class="plans">
<div class="plan rv"><h3>{T('Free plan', '免費版')}</h3><div class="price">{T('Free', '免費')}</div><a class="btn btn--2" href="{APP}/">{T('Start free', '免費開始')}</a></div>
<div class="plan plan--pro rv" style="--rd:.1s"><h3>{T('Premium', '完整版')}</h3><div class="price">{price_html(lang, T('a month', '每月'))}</div><p class="trial">{T('7 days free', '免費試用 7 日')}</p><a class="btn" href="{APP}/">{T('Start 7 days free', '免費試用 7 日')}</a></div>
</div>
<p class="vnote">{T('7 days free, then billed monthly. Cancel in Settings.', '免費試用 7 日，之後按月收費。可以喺設定取消。')}{hk}</p>
</div></section>

<section class="sec sec--wash" id="faq"><div class="wrap">
<div class="open"><h2 class="rv">{T('Questions, answered plainly', '常見問題，直接答你')}</h2></div>
<div class="faq">{faq}</div></div></section>

<section class="final" data-final><div class="wrap">
<h2 class="rv">{T("Ready for today?", '今日準備好未？')}</h2>
<a class="btn btn--lg" href="{APP}/">{T('Start free', '免費開始')}</a>
<div class="pup" aria-hidden="true"><img class="treat" src="/img/icons/bone.webp" width="128" height="128" alt=""><span class="sprite" data-clip="idle" data-hover="wiggle"></span></div>
</div></section>
</main>
"""
    return h + body + '<script defer src="/js/cost.js"></script>\n' + footer(lang, demos=True)
