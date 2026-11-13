"""The home page, English and Cantonese. Copy sits next to its translation: T("English", "廣東話")."""
import json
import re
import parts
from cost import cost_section
from parts import NEED_PAGES, NEED_UI, VS_PAGES, vs_slug, u, FACTS, NUM_WORD, NUM_YUE, LANG_COUNT, APP, MAIL, SITE, esc, footer, head, header, mk, price_html, price_text, LANGS, PRICES

ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent
CMP = json.loads((ROOT / "scripts" / "competitors.json").read_text())
PQ = json.loads((ROOT / "content" / "practice-quality.json").read_text())  # requires_feature: practice_quality
ROWS_ORDER = None

# Cantonese for the short notes in the comparison table (keyed by the English note).
ZHN = {
    "$29.99 per month (monthly plan); first two weeks free; 30-day money-back guarantee; currency not named": "每月 $29.99（月費計劃）；頭兩星期免費；30 日退款保證；冇講貨幣",
    "$89.99 USD for Language Therapy 4-in-1; free Lite version; billing model not stated on the page": "Language Therapy 4-in-1 售 US$89.99；有免費 Lite 版；頁面冇講收費模式",
    "CT app $29.99/month; FitMi $399; remote programme $99/month; currency not named": "CT app 每月 $29.99；FitMi $399；遠程課程每月 $99；冇講貨幣",
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
    "Free account and exercises": "免費帳戶同練習",
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
    "price": (("yes", "Free to start; Premium US$9.99 a month, 7 days free"), ("yes", "免費開始；完整版每月 HK$78（US$9.99），免費試用 7 日")),
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
    mo = t("month", "月")
    pc = lambda x, sub="": f'<td><span class="mk t">{x}</span>{f"<small>{sub}</small>" if sub else ""}</td>'
    rows += (f'<tr class="pricerow"><th scope="row">{t("Price", "價錢")}</th>'
             f'<td class="us"><span class="mk t y">{PRICES["usd"]} / {mo}</span><small>{t("Free plan", "免費版")}</small></td>'
             + pc(f"$29.99 / {mo}") + pc("$89.99", t("4-in-1 app", "四合一 app")) + pc(t("Free", "免費")) + '</tr>')
    legend = t("\u2713 yes, Part = partly, \u2013 not offered as far as we can tell.", "\u2713 有，部分 = 部分有，\u2013 據我哋所知冇提供。")
    return f"""<div class="cmpwrap" role="region" tabindex="0" aria-label="{t('Comparison table', '比較表')}"><table class="cmp cmp--s"><thead><tr><th scope="col"><span class="sr">{t('Feature', '項目')}</span></th><th scope="col" class="us">Bonet</th>{th}</tr></thead><tbody>{rows}</tbody></table></div>
<p class="asof">{legend} {t('As of November 2026.', '資料截至 2026 年 11 月。')} <a href="/compare.html">{t('Notes and sources', '附註同來源')}</a></p>
<p class="asof">{t('One product at a time:', '逐個產品比較：')} {" &middot; ".join(f'<a href="/{vs_slug(s)}">{t("Bonet vs {name}", "哥基健動同 {name} 比較").replace("{name}", n)}</a>' for s, n in VS_PAGES.items())}</p>"""

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
    asof3 = t("Prices are what each company's own page showed on 13 November 2026. What they include differs: Constant Therapy and Tactus Therapy offer large, clinically developed exercise libraries, and Constant Therapy also has a clinician app. Bonet is a smaller home practice app with fewer exercises.", "價錢係各公司自己頁面喺 2026 年 11 月 13 日顯示嘅價錢。包含嘅內容唔同：Constant Therapy 同 Tactus Therapy 有龐大、由臨床人員發展嘅練習庫，Constant Therapy 仲有臨床人員 app。哥基健動係較細嘅居家練習 app，練習數量較少。")
    asof2 = t("Bonet has not been tested in a clinical trial and is not a medical device. How long each company has been in the market was not stated on the pages we read, so we make no claim about it.", "哥基健動未經臨床試驗，亦唔係醫療器材。各公司入市幾耐，我哋睇過嘅頁面冇講明，所以唔作比較。")
    return f"""<div class="cmpwrap" role="region" tabindex="0" aria-label="{t('Comparison table, scrolls sideways on small screens', '比較表，細螢幕可以左右捲動')}"><table class="cmp"><thead><tr><th scope="col"><span class="sr">{t('Feature', '項目')}</span></th><th scope="col" class="us">Bonet</th>{th}</tr></thead><tbody>{rows}</tbody></table></div>
<p class="asof">{asof}</p>
<p class="asof">{asof3}</p>
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


VIDEO_ON = False  # set by build-site.py from content/flags.json new_demo_video (or --with new_demo_video)


def video_section(T, lang, vid):
    """Flagged section: per-language film. preload="none" so no film bytes load until the visitor presses play."""
    vtt = f'<track kind="captions" src="{vid["vtt"]}" srclang="{LANGS[lang]["tag"]}" label="{LANGS[lang]["name"]}" default>' if vid["vtt"] else ""
    return f"""<section class="sec sec--blue" id="video"><div class="wrap">
<div class="open open--c"><h2 class="rv">{T('See Bonet in action', '睇下哥基健動點用')}</h2></div>
<div class="player rv-tilt" data-player><video preload="none" controls playsinline poster="{vid["poster"]}"><source src="{vid["src"]}" type="video/mp4">{vtt}</video><button type="button" class="play" aria-label="{T('Play the demo video', '播放示範影片')}"></button></div>
</div></section>
"""


def video_for(lang):
    """Per-language demo video, decided at build time from the files present (no 404s); falls back to English."""
    d = ROOT / "media" / "demo"
    code = lang
    if not (d / f"bonet-demo-{code}.mp4").exists():
        code = "en"
    poster = f"bonet-demo-{code}.jpg" if (d / f"bonet-demo-{code}.jpg").exists() else "bonet-demo-en.jpg"
    vtt = f"/media/demo/bonet-demo-{code}.vtt" if (d / f"bonet-demo-{code}.vtt").exists() else ""
    return {"src": f"/media/demo/bonet-demo-{code}.mp4", "poster": f"/media/demo/{poster}", "vtt": vtt}


def home(lang):
    T = mk(lang)
    base = LANGS[lang]["path"]
    title = T("Bonet: home practice app for seniors and after a stroke", "哥基健動 Bonet：長者同中風後嘅居家練習 app")
    desc = T("Daily home practice for older adults, including after a stroke: camera-counted exercises, speech practice and brain games. Free to start. Not a medical device.",
             "為長者而設嘅每日居家練習，中風後都用得：鏡頭數次數嘅運動、說話練習同腦力遊戲。免費開始。唔係醫療器材。")
    usd = re.match(r"[^\d]*([\d.]+)", PRICES["usd"]).group(1)
    FXL = lambda x: x.replace("{levels}", str(FACTS["speaking_levels"])).replace("{exercises}", str(FACTS["exercises"]))
    ld = [
        {"@context": "https://schema.org", "@type": "Organization", "@id": SITE + "/#organization", "name": "Coglix Labs Inc.", "url": SITE + "/", "logo": SITE + "/icon-512.png", "email": MAIL},
        {"@context": "https://schema.org", "@type": "SoftwareApplication", "@id": SITE + "/#software", "name": "Bonet", "alternateName": "哥基健動", "url": SITE + "/",
         "image": SITE + "/img/" + ("og-en.png" if lang == "en" else "og-zh.png"), "applicationCategory": "LifestyleApplication", "operatingSystem": "Web browser",
         "inLanguage": [x["tag"] for x in LANGS.values()], "description": desc, "publisher": {"@id": SITE + "/#organization"},
         "featureList": [FXL(T("All {exercises} exercises, your own plans", "全部 {exercises} 個運動，仲可以自訂計劃")), FXL(T("All {levels} speaking levels", "全部 {levels} 級說話練習")), T("Every brain game level", "所有腦力遊戲級別")],
         "offers": [{"@type": "Offer", "name": T("Free plan", "免費版"), "price": "0", "priceCurrency": "USD", "url": APP + "/"},
                    {"@type": "Offer", "name": T("Premium", "完整版"), "price": usd, "priceCurrency": "USD", "url": APP + "/",
                     "description": T("7 days free, then billed monthly. Cancel in Settings.", "免費試用 7 日，之後按月收費。可以喺設定取消。"),
                     "priceSpecification": {"@type": "UnitPriceSpecification", "price": usd, "priceCurrency": "USD", "billingDuration": "P1M"}}]},
        {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Bonet", "alternateName": "哥基健動",
         "inLanguage": [x["tag"] for x in LANGS.values()], "publisher": {"@id": SITE + "/#organization"}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).replace("{price}", price_text(lang))}} for q, a in faq_items(lang)]},
    ]
    extra = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
    h = head(lang, title, desc, SITE + base, "og-en.png" if lang == "en" else "og-zh.png", extra=extra, alt={c: SITE + d["path"] for c, d in LANGS.items()})
    h += header(lang)
    price = price_text(lang)
    vid = video_for(lang)
    day = "33 cents" if lang == "en" else "US$%.2f" % (float(re.match(r"[^\d]*([\d.]+)", PRICES["usd"]).group(1)) / 30)

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
    hk = ""  # the Hong Kong dollar note lives on /subscriptions and on the Cantonese page (prices.json show_hkd_note_on), not on this page
    # Free and Premium lists: every row checked against app/web/src/lib/limits.ts (see README, "Pricing facts")
    FX = lambda x: x.replace("{levels}", str(FACTS["speaking_levels"])).replace("{exercises}", str(FACTS["exercises"])).replace("{free_ex}", str(FACTS["free_exercises"]))
    free = [FX(T("Speaking levels 1 to 3 of {levels}", "說話第 1 至 3 級（共 {levels} 級）")), FX(T("{free_ex} of {exercises} exercises", "{exercises} 個運動揀 {free_ex} 個")), T("Brain games on Easy", "腦力遊戲簡單級"),
            T("Last 7 days of progress", "最近 7 日嘅進度"), T("Report for the last 2 weeks", "最近 2 星期嘅報告"), T("Streak, league, outfits", "連續練習、聯賽、換衫")]
    prem = [FX(T("All {levels} speaking levels", "全部 {levels} 級說話練習")), FX(T("All {exercises} exercises, your own plans", "全部 {exercises} 個運動，仲可以自訂計劃")), T("Every brain game level", "所有腦力遊戲級別"),
            T("Full history and report", "完整歷史同報告"), T("Everything in Free", "免費版嘅全部功能")]
    li = lambda xs: "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
    perday = T("about {day} a day", "約 {day} 一日").replace("{day}", day)
    P = lambda k: T(PQ[k][0], PQ[k][1])
    pq = ""
    if False:
        pq = f"""<!-- requires_feature: practice_quality -->
<section class="sec sec--blue" id="quality"><div class="wrap">
<div class="open open--c">{word(P('h2'), 'chart')}<p class="kicker rv">{P('kicker')}</p></div>
<div class="duo">
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('qmove', T('Animated preview: after a set, a six-sided chart draws itself and moves from last time to today, then a tip card slides in.', '動畫預覽：做完一組，六角形圖表逐邊畫出，由上次變成今次，跟住出現提示卡。'))}</div><div class="tcap"><h3>{P('move_h')}</h3></div></div>
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('qspeak', T('Animated preview: after speaking practice, a six-sided chart of words heard, pace and pauses moves from last time to today.', '動畫預覽：說話練習之後，聽到嘅詞語、速度同停頓六角形圖表由上次變成今次。'))}</div><div class="tcap"><h3>{P('speak_h')}</h3></div></div>
</div>
<p class="note" style="margin-top:2rem">{P('caveat')}</p>
</div></section>
<!-- /requires_feature -->
"""
    DS = json.loads((ROOT / "content" / "demo-strings.json").read_text())

    def D(en):
        """Label from the demo strings (already written for all eight languages)."""
        return en if lang == "en" else DS.get(en, {}).get(lang, en)

    def icon(n, cls=""):
        return f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="/img/icons/{n}.webp" width="128" height="128" alt="" loading="lazy">'

    def hexsvg(labels, last, today):
        import math
        c, r = 150, 100
        pt = lambda i, v: (c + math.cos(-math.pi / 2 + i * math.pi / 3) * r * v, c + math.sin(-math.pi / 2 + i * math.pi / 3) * r * v)
        poly = lambda vs: " ".join("%.1f,%.1f" % pt(i, v) for i, v in enumerate(vs))
        g = "".join(f'<polygon points="{poly([k] * 6)}" fill="none" stroke="#e5e7eb" stroke-width="2"/>' for k in (.25, .5, .75, 1))
        g += "".join('<line x1="150" y1="150" x2="%.1f" y2="%.1f" stroke="#e5e7eb" stroke-width="2"/>' % pt(i, 1) for i in range(6))
        g += f'<polygon points="{poly(last)}" fill="rgba(107,116,132,.12)" stroke="#6b7484" stroke-width="2.5" stroke-dasharray="6 6"/>'
        g += f'<polygon points="{poly(today)}" fill="rgba(31,138,230,.22)" stroke="#1f8ae6" stroke-width="4" stroke-linejoin="round"/>'
        g += "".join('<circle cx="%.1f" cy="%.1f" r="5.5" fill="#1f8ae6"/>' % pt(i, v) for i, v in enumerate(today))
        g += "".join('<text x="%.1f" y="%.1f" text-anchor="middle" dominant-baseline="middle" font-size="16" font-weight="900" fill="#3f4a5a">%s</text>' % (*pt(i, 1.27), l) for i, l in enumerate(labels))
        return f'<svg viewBox="0 0 300 300" width="100%" aria-hidden="true">{g}</svg>'

    MV = ([D(x) for x in ("Range", "Pace", "Steady", "L/R", "Hold", "Done")], [.55, .6, .5, .45, .5, .7], [.7, .65, .62, .55, .6, .85])
    SP = ([D(x) for x in ("Heard", "No hints", "Pace", "Pauses", "Start time", "Steady")], [.5, .35, .55, .5, .45, .5], [.65, .5, .6, .62, .55, .6])

    def report_mock():
        mins = [10, 0, 15, 15, 0, 10, 20, 15, 15, 0, 20, 15, 20, 25]
        top = max(mins)
        bars = "".join(f'<i style="height:{max(m, 1) / top * 100:.0f}%;--i:{n}"{" class=zero" if not m else ""}></i>' for n, m in enumerate(mins))
        rows = "".join(f"<tr><th scope=\"row\">{l}</th><td>{round(a * 100)}</td><td>{round(b * 100)}</td></tr>" for l, a, b in zip(MV[0], MV[1], MV[2]))
        fam = "".join(f'<div><dd>{n}</dd><dt>{l}</dt></div>' for l, n in ((T("New", "新嘅"), 12), (T("Learning", "學緊"), 9), (T("Familiar", "熟咗"), 21)))
        tot = sum(mins)
        return f"""<div class="rpt rv">
<div class="rpt-top"><img src="/img/mascot/point.webp" width="512" height="512" alt=""><div><h3>{T('Home practice report', '居家練習報告')}</h3><small>{T('Last 2 weeks', '最近 2 星期')}</small></div><span class="rpt-tag">{T('Sample data', '示範資料')}</span></div>
<dl class="rpt-sum"><div><dt>{T('Days practised', '練習日數')}</dt><dd>{sum(1 for m in mins if m)}</dd></div><div><dt>{T('Minutes', '分鐘')}</dt><dd>{tot}</dd></div><div><dt>{D('day streak')}</dt><dd>5</dd></div></dl>
<div class="rpt-hex">
<div><h4>{D('Move')}</h4>{hexsvg(*MV)}<table><thead><tr><th></th><th>{D('Last time')}</th><th>{D('Today')}</th></tr></thead><tbody>{rows}</tbody></table></div>
<div><h4>{D('Speak')}</h4>{hexsvg(*SP)}<h5>{T('Familiarity', '熟悉程度')}</h5><dl class="rpt-fam">{fam}</dl></div>
</div>
<div class="rpt-low"><div><h4>{D('Minutes practised each day')}</h4><div class="rpt-bars">{bars}</div></div>
<div><h4>{T('Tips given', '俾過嘅提示')}</h4><ul><li>{D('Lift a little higher on your left side.')}</li><li>{D('Take a breath before long sentences.')}</li></ul></div></div>
<p class="rpt-note">{P('caveat')}</p>
</div>"""

    def result_row(name, label, flip):
        return f"""<div class="feat feat--res{' feat--flip' if flip else ''}">
<div class="feat-copy"><h3 class="rv res-h">{T('How this session went, next to last time', '今次做得點，同上次比較')}</h3><p class="line rv">{T('What to work on next', '下一步練習啲乜')}</p></div>
<div class="feat-art">{card(name, label)}</div>
</div>"""

    pre = "" if LANGS[lang]["path"] == "/" else LANGS[lang]["path"].rstrip("/")
    why = [("today", T("Three kinds of practice, one plan", "三種練習，一個計劃"), T("Movement, speaking and brain games share one daily plan.", "運動、說話同腦力遊戲，共用一個每日計劃。")),
           ("fire", T("Made to come back to", "想日日返嚟"), T("A daily path, a streak, a weekly league and a corgi to dress up.", "每日路徑、連續練習、每週聯賽，仲有隻可以換衫嘅柯基。")),
           ("ear", T("Feedback made for you", "為你而設嘅回饋"), T("Specific to each session: how high, how steady, which words.", "每次練習都不同：幾高、幾穩、邊啲詞語。")),
           ("chart", T("A report your therapist can read", "治療師睇得明嘅報告"), T("Tracked over time, so you can see the change.", "長期記錄，睇得到變化。"))]
    whyh = "".join(f'<div class="why-i rv" style="--rd:{n * .08:.2f}s">{icon(i)}<h3>{a}</h3><p>{b}</p></div>' for n, (i, a, b) in enumerate(why))
    who = [("sun", T("Older adults keeping active every day", "每日保持活動嘅長者"), "/exercise-app-for-seniors"),
           ("footprints", T("Practising at home after a stroke or injury", "中風或受傷後喺屋企練習"), "/stroke-home-practice"),
           ("calendar", T("Between physio or speech therapy visits", "物理治療或言語治療覆診之間"), "/speech-practice-at-home"),
           ("brain", T("Regular memory and attention practice", "定期練習記憶同專注"), None),
           ("heart", T("Families and carers helping out", "幫手嘅家人同照顧者"), "/for-family-and-carers")]
    whoh = "".join(f'<li class="rv"><a class="wc" href="{h}">{icon(i)}<span>{x}</span></a></li>' if h else f'<li class="rv"><span class="wc">{icon(i)}<span>{x}</span></span></li>' for i, x, h in who)
    need_links = " &middot; ".join(f'<a href="/{p}">{u(NEED_UI[p], lang)}</a>' for p in NEED_PAGES)
    whoh += f'<li class="rv"><a class="wc" href="/therapist.html">{icon("chart")}<span>{T("Therapists following home practice", "跟進居家練習嘅治療師")}</span></a></li>'
    final_price = T("Free to start. Premium {price} a month, 7 days free.", "免費開始。完整版每月 {price}，免費試用 7 日。").replace("{price}", price)

    def feat_sec(kind, flip, word_html, k1, k2, big, resname, reslabel):
        res = result_row(resname, reslabel, not flip) if (pq_on and resname) else ""
        return f"""<div class="feat{' feat--flip' if flip else ''}">
<div class="feat-copy">{word_html}
<p class="kicker rv">{k1}</p><p class="line rv">{k2}</p></div>
<div class="feat-art">{big}</div>
</div>
{res}"""

    mv_alt = T('Animated preview: after a set, a six-sided chart draws itself and moves from last time to today, then a tip card slides in.', '動畫預覽：做完一組，六角形圖表逐邊畫出，由上次變成今次，跟住出現提示卡。')
    sp_alt = T('Animated preview: after speaking practice, a six-sided chart of words heard, pace and pauses moves from last time to today.', '動畫預覽：說話練習之後，聽到嘅詞語、速度同停頓六角形圖表由上次變成今次。')
    how = "".join([
        feat_sec("move", False, word(T('Move', '運動'), 'muscle'),
                 T('Arms and shoulders, hands, sit-to-stand, legs and balance.', '手臂同肩膀、手部、坐到站、雙腿同平衡。'),
                 T('A 3D guide shows the move.', '立體示範教你點做。') + " " + T('The camera counts each rep.', '鏡頭幫你數每一下。'),
                 card('move', T('Animated preview of the exercise screen counting 1, 2, 3 reps beside a 3D guide.', '動畫預覽：運動畫面一邊有立體示範，一邊數 1、2、3 下。')), 'qmove', mv_alt),
        '<div class="feat-gap"></div>',
        feat_sec("speak", True, word(T('Speak', '說話'), 'speak'),
                 T('Say words, name pictures, build sentences, listen.', '講詞語、認圖片、砌句子、聽說話。'),
                 T('Stuck? Hints grow one step at a time.', '唔識講？提示一步一步加大。'),
                 card('speak', T('Animated preview: word tiles move into place to build a sentence and Great! appears.', '動畫預覽：詞語磚砌成句子，然後出現「好呀！」。')), 'qspeak', sp_alt),
        '<div class="feat-gap"></div>',
        feat_sec("think", False, word(T('Think', '腦力'), 'brain', 'display--or'),
                 T('Memory, attention and quick thinking, in six games.', '記憶、專注同反應，六款遊戲。'),
                 T('Difficulty adjusts to how you do.', '難度會跟你做得點而調整。'),
                 card('brain', T('Animated preview: two cards flip and match in a pairs game.', '動畫預覽：配對遊戲入面兩張牌翻開並且配成一對。')), None, None),
    ])
    def panel(key, word_html, k1, steps_html, art):
        return f"""<div class="panel" role="tabpanel" id="p-{key}" aria-labelledby="t-{key}" tabindex="0">
<div class="panel-copy">{word_html}<p class="kicker rv">{k1}</p>{steps_html}</div>
<div class="panel-art">{art}</div>
</div>"""

    def steps(*xs):
        return '<ol class="steps">' + "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in xs) + "</ol>"

    def tab(key, ico, label, sel):
        return f'<button type="button" role="tab" id="t-{key}" aria-controls="p-{key}" aria-selected="{"true" if sel else "false"}" tabindex="{0 if sel else -1}">{icon(ico)}<span>{label}</span></button>'

    practice_sec = f"""<section class="sec sec--wash" id="practice"><span id="how"></span><div class="wrap">
<div class="open open--c"><h2 class="display display--ink rv-word">{T('What you practise', '你會練習啲乜')}</h2></div>
<div class="tabs" data-tabs>
<div class="tablist" role="tablist" aria-label="{T('What you practise', '你會練習啲乜')}">{tab('move', 'muscle', T('Move', '運動'), True)}{tab('speak', 'speak', T('Speak', '說話'), False)}{tab('think', 'brain', T('Think', '腦力'), False)}</div>
<div class="panels">
{panel('move', word(T('Move', '運動'), 'muscle'), T('Arms and shoulders, hands, sit-to-stand, legs and balance.', '手臂同肩膀、手部、坐到站、雙腿同平衡。'),
       steps((T('See it', '睇示範'), T('A 3D guide shows the move.', '立體示範教你點做。')), (T('Do it', '跟住做'), T('The camera counts each rep.', '鏡頭幫你數每一下。')), (T('Get a tip', '有個小提示'), T('Height, steadiness, left and right. The next plan adjusts.', '幅度、穩定、左右。下一個計劃會跟住調整。'))),
       card('move', T('Animated preview of the exercise screen counting 1, 2, 3 reps beside a 3D guide.', '動畫預覽：運動畫面一邊有立體示範，一邊數 1、2、3 下。')))}
{panel('speak', word(T('Speak', '說話'), 'speak'), T('Say words, name pictures, build sentences, listen.', '講詞語、認圖片、砌句子、聽說話。'),
       steps((T('Say it', '開口講'), T('Pick a level and say the words aloud.', '揀個級別，大聲講出嚟。')), (T('Get a hint', '有提示'), T('Stuck? Hints grow one step at a time.', '唔識講？提示一步一步加大。')), (T('See what it heard', '睇佢聽到乜'), T('Words heard, pace and pauses. Items return for review.', '聽到嘅詞語、速度、停頓。未熟嘅會再出現複習。'))),
       card('speak', T('Animated preview: word tiles move into place to build a sentence and Great! appears.', '動畫預覽：詞語磚砌成句子，然後出現「好呀！」。')))}
{panel('think', word(T('Think', '腦力'), 'brain', 'display--or'), T('Memory, attention and quick thinking, in six games.', '記憶、專注同反應，六款遊戲。'),
       steps((T('Play a round', '玩一局'), T('Short rounds you can start any time.', '短短一局，隨時開始。')), (T('It follows you', '難度跟住你'), T('Difficulty adjusts to how you do.', '難度會跟你做得點而調整。')), (T('See results', '睇結果'), T('Your results over time.', '你嘅結果，一路睇住變化。'))),
       card('brain', T('Animated preview: two cards flip and match in a pairs game.', '動畫預覽：配對遊戲入面兩張牌翻開並且配成一對。')))}
</div></div>
<p class="calm rv"><a href="/practice">{T('See every exercise, speaking practice and brain game', '睇晒所有運動、說話練習同腦力遊戲')}</a></p>
</div></section>"""

    if pq_on:
        mins = [10, 0, 15, 15, 0, 10, 20, 15, 15, 0, 20, 15, 20, 25]
        bars = "".join(f'<i style="height:{max(m, 1) / max(mins) * 100:.0f}%"{" class=zero" if not m else (" class=new" if n == len(mins) - 1 else "")}></i>' for n, m in enumerate(mins))
        hexmini = hexsvg(MV[0], MV[1], MV[2]).replace('width="100%"', 'width="64" height="64"').replace('font-size="16"', 'font-size="0"')
        c2 = f"""<div class="fb-tip"><img src="/img/mascot/point.webp" width="512" height="512" alt="">
<b>{D('A tip for next time')}</b><p>{D('Lift a little higher on your left side.')}</p>
<div class="fb-plan" aria-hidden="true"><span class="on"><img src="/img/icons/muscle.webp" width="128" height="128" alt=""></span><span><img src="/img/icons/speak.webp" width="128" height="128" alt=""></span><span><img src="/img/icons/brain.webp" width="128" height="128" alt=""></span><em>{T("Tomorrow's plan adjusts", '聽日嘅計劃會跟住調整')}</em></div></div>"""
        c3 = f"""<a class="fb-paper" href="/example-report" aria-label="{T('See a full sample report', '睇完整示範報告')}">
<span class="fb-ptop"><img src="/img/mascot/point.webp" width="512" height="512" alt=""><b>{T('Home practice report', '居家練習報告')}</b></span>
<small class="fb-sample">{T('Sample data', '示範資料')} &middot; {T('Last 2 weeks', '最近 2 星期')}</small>
<span class="fb-psum"><span><small>{T('Days practised', '練習日數')}</small><b>{sum(1 for m in mins if m)}</b></span><span><small>{T('Minutes', '分鐘')}</small><b>{sum(mins)}</b></span><span>{hexmini}</span></span>
<span class="fb-pbars">{bars}</span>
<span class="fb-saved">&#10003; {D('Saved')}</span></a>"""
        col = lambda n, vis, title, line, extra="": f'<div class="fb-col rv" style="--rd:{n * .35:.2f}s"><div class="fb-vis">{vis}</div><h3>{title}</h3><p>{line}</p>{extra}</div>'
        feedback_sec = f"""<section class="sec sec--blue" id="feedback"><div class="wrap">
<div class="open open--c"><h2 class="display display--ink rv-word">{T('See how it went. Share it with your therapist.', '睇下做得點，再俾治療師睇。')}</h2><p class="kicker rv">{T('Every session gets a picture, a next step and a place in your report.', '每次練習都有一幅圖、一個下一步，同埋記入你嘅報告。')}</p></div>
<div class="fb3">
{col(0, '<div class="card-demo" data-ss-fill>' + demo('qmove', mv_alt) + '</div>', T('A picture of each session', '每次練習一幅圖'), T('How this session went, next to last time', '今次做得點，同上次比較'))}
{col(1, c2, T('One thing to work on', '一件要練習嘅事'), T('A specific tip after every session. The next daily plan adjusts to it.', '每次練習後都有具體提示，下一個每日計劃會跟住調整。'))}
{col(2, c3, T('Ready for your therapist', '俾治療師睇都得'), T('Every session is saved to your progress and your shareable report.', '每次練習都儲存喺你嘅進度同可以分享嘅報告入面。'), f'<a class="fb-more" href="/example-report">{T("See a full sample report", "睇完整示範報告")}</a>')}
</div>
<p class="note res-note">{P('caveat')}</p>
</div></section>"""
    else:
        feedback_sec = f"""<section class="sec sec--blue" id="feedback"><div class="wrap">
<div class="feat">
<div class="feat-copy"><h2 class="display rv-word">{T('Progress you can see.', '睇得到嘅進度。')}</h2>
<p class="kicker rv">{T('Share a one-page report with your therapist or family.', '一頁報告，可以俾治療師或者家人睇。')}</p></div>
<div class="feat-art"><div class="card-demo rv-tilt" data-ss-fill>{demo('progress', T('Animated preview: a weekly progress chart drawing in.', '動畫預覽：每週進度圖表逐條畫出。'))}</div>
<div class="paper rv" aria-hidden="true"><img src="/img/mascot/point.webp" width="512" height="512" alt=""><h4>{T('Home practice report', '居家練習報告')}</h4><small>{T('Last 2 weeks', '最近 2 星期')}</small>
<div class="bars rv-bars">{''.join(f'<i style="height:{x}%;--i:{n}"></i>' for n, x in enumerate([45, 70, 30, 85, 60, 95, 75]))}</div><div class="ln"></div><div class="ln m"></div><div class="ln s"></div></div></div>
</div></div></section>"""
    note_pq = f'<p class="note res-note">{P("caveat")}</p>' if pq_on else ""
    body = f"""<main id="main">
<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<h1>{h1}</h1>
<p class="sub">{T('Daily practice for older adults, including after a stroke.', '為長者而設嘅每日練習，中風後都用得。')} {T('Every session tracked, with feedback made for you.', '每次練習都有紀錄，仲有為你而設嘅回饋。')}</p>
<div class="cta-row"><a class="btn btn--lg" href="{APP}/">{T('Start free', '免費開始')}</a><a class="btn btn--2 btn--lg" href="#practice">{T('See how it works', '睇下點用')}</a></div>
<p class="priceline">{T('Free to start. Premium {price} a month, about {day} a day.', '免費開始。完整版每月 {price}，約 {day} 一日。').replace('{price}', price).replace('{day}', day)}</p>
</div>
<div class="hero-art" data-ss-fill>
<span class="fl" style="left:4%;top:8%;width:2.6rem;--k:18" data-par><img src="/img/icons/star.webp" width="128" height="128" alt=""></span>
<div class="corgi" data-corgi role="img" aria-label="{T('Bonet the corgi', '朱古力')}"><button type="button" class="pupbtn" data-hover="wiggle" tabindex="-1" aria-hidden="true"><span class="sprite" data-clip="wave" data-then="idle" data-loops="2" data-rest="idle"></span></button></div>
{demo('hero', T('Animated preview: tap Start on the Today path, the camera counts three arm raises, Great set, and the step is ticked.', '動畫預覽：喺「今日」路徑撳開始，鏡頭數三下舉手，完成一組，然後打咗剔。'))}
</div></div></section>

<section class="sec" id="why"><div class="wrap"><div class="why">{whyh}</div></div></section>

{practice_sec}

{feedback_sec}

<section class="sec"><div class="wrap">
<div class="open open--c">{word(T('Come back tomorrow.', '聽日再嚟。'), 'fire', 'display--ink')}</div>
<div class="trio">
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('streak', T('Animated preview: a streak calendar where a saver covers a missed day.', '動畫預覽：連續練習日曆，保護盾補返漏咗嗰日。'))}</div><div class="tcap"><h3>{T('Keep your streak', '保持連續練習')}</h3></div></div>
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('league', T('Animated preview: a weekly league where your row climbs after practice.', '動畫預覽：每週聯賽，練習後你嘅名次上升。'))}</div><div class="tcap"><h3>{T('Weekly league', '每週聯賽')}</h3></div></div>
<div class="rv-tilt"><div class="card-demo" data-ss-fill data-wardrobe>{demo('wardrobe', T('Animated preview: Bonet the corgi trying on a bandana, a bow tie, a cap and a crown.', '動畫預覽：朱古力試戴頸巾、領結、棒球帽同小皇冠。'))}</div><div class="tcap"><h3>{T('Dress up Bonet', '幫朱古力換衫')}</h3></div></div>
</div></div></section>

<section class="sec" id="plans"><div class="wrap">
<div class="open open--c"><h2 class="display display--ink rv-word">{T('Start free.', '免費開始。')}</h2><p class="kicker rv">{T('Priced for everyday use: {price} a month, about {day} a day.', '日常用得起嘅價錢：每月 {price}，約 {day} 一日。').replace('{price}', price).replace('{day}', day)}</p></div>
<div class="plans">
<article class="plan rv"><h3>{T('Free plan', '免費版')}</h3><p class="price">{T('Free', '免費')}</p>{li(free)}<a class="btn btn--2 btn--lg" href="{APP}/">{T('Start free', '免費開始')}</a></article>
<article class="plan plan--pro rv" style="--rd:.1s"><h3>{T('Premium', '完整版')}</h3><p class="price">{price_html(lang, T('a month', '每月'))}</p><p class="trial">{perday}. {T('7 days free', '免費試用 7 日')}</p>{li(prem)}<a class="btn btn--lg" href="{APP}/">{T('Start 7 days free', '免費試用 7 日')}</a><p class="canc"><a href="/subscriptions">{T('Cancel any time', '隨時可取消')}</a></p></article>
</div>
<p class="vnote">{T('7 days free, then billed monthly. Cancel in Settings.', '免費試用 7 日，之後按月收費。可以喺設定取消。')}{hk}</p>
</div></section>

<section class="sec" id="compare"><div class="wrap">
<div class="open open--c"><h2 class="display display--ink rv-word">{T('How Bonet compares', '同其他方案比較')}</h2></div>
{compare(lang)}
</div></section>

{cost_section(lang)}

<section class="sec" id="who"><div class="wrap">
<div class="open open--c"><h2 class="display display--ink rv-word">{T('Who Bonet is for', '哥基健動啱邊啲人')}</h2></div>
<ul class="who">{whoh}</ul>
<p class="calm rv">{need_links}</p>
<p class="calm rv">{T('Bonet is a practice tool. It is not a medical device and does not diagnose or treat. Ask your doctor or therapist what practice is right for you.', '哥基健動係練習工具，唔係醫療器材，亦唔會診斷或者治療。邊啲練習啱你，請問你嘅醫生或者治療師。')} <a href="{pre}/safety">{T('Privacy and safety', '私隱與安全')}</a></p>
</div></section>

<section class="sec sec--blue"><div class="wrap">
<div class="open open--c">{word(T('Big. Calm. Easy.', '大字。清晰。簡單。'), 'sun')}</div>
<div class="duo">
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('simple', T('Animated preview: turning on Simple mode changes a busy list into one big Start button.', '動畫預覽：開啟簡單模式，一堆選項變成一個大大嘅開始掣。'))}</div><div class="tcap"><h3>{T('Simple mode', '簡單模式')}</h3></div></div>
<div class="rv-tilt"><div class="card-demo" data-ss-fill>{demo('lang', T(f'Animated preview: a greeting changes through {NUM_WORD[LANG_COUNT].lower()} languages.', f'動畫預覽：問候語轉換{NUM_YUE[LANG_COUNT]}種語言。'))}</div><div class="tcap"><h3>{T(f'{NUM_WORD[LANG_COUNT]} languages', f'{NUM_YUE[LANG_COUNT]}種語言')}</h3></div></div>
</div>
<p class="safe rv">{T('Camera video stays on your device. <span>Bonet is not a medical device.</span>', '鏡頭影像只留喺你部機。<span>哥基健動唔係醫療器材。</span>')} <a href="{pre}/safety">{T('Privacy and safety', '私隱與安全')}</a></p>
</div></section>

<section class="sec sec--wash" id="faq"><div class="wrap">
<div class="open open--c"><h2 class="rv">{T('Questions, answered plainly', '常見問題，直接答你')}</h2></div>
<div class="faq">{faq}</div></div></section>

{video_section(T, lang, vid) if VIDEO_ON else ""}

<section class="final" data-final><div class="wrap">
<span class="fi fi1"><img src="/img/icons/star.webp" width="128" height="128" alt=""></span><span class="fi fi2"><img src="/img/icons/heart.webp" width="128" height="128" alt=""></span><span class="fi fi3"><img src="/img/icons/bone.webp" width="128" height="128" alt=""></span>
<div class="final-stage">
<div class="fpup" role="img" aria-label="{T('Bonet the corgi', '朱古力')}"><button type="button" class="pupbtn" data-hover="cheer" tabindex="-1" aria-hidden="true"><span class="sprite" data-seq="tilt,wiggle,wave,idle" data-rest="idle"></span></button><i class="gshadow"></i></div>
<div class="final-say">
<h2 class="rv">{T("Ready when you are.", '你準備好就開始。')}</h2>
<p class="bubble rv">{T("Just a few minutes. I'll count.", '幾分鐘就夠，我幫你數。')}</p>
<a class="btn btn--lg" href="{APP}/">{T('Start free', '免費開始')}</a>
<p class="priceline">{final_price}</p>
</div></div>
</div></section>

</main>
"""
    return h + body + '<script defer src="/js/cost.js"></script>\n' + footer(lang, demos=True)
