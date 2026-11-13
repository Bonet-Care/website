#!/usr/bin/env python3
"""
Builds the marketing home page in both languages from one template:
  index.html     (English)
  zh/index.html  (Traditional Chinese)

Edit copy in STRINGS, layout in TEMPLATE, styles in css/site.css, then run:
  python3 scripts/build-home.py
SEO tags, analytics and JSON-LD live in partials/head-{en,zh}.html.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT  # the site lives at the repo root

STRINGS = {
    "brand": ("Bonet", "哥基健動"),
    "skip": ("Skip to content", "跳至內容"),
    "nav_practice": ("Practice", "練習"),
    "nav_how": ("How it works", "運作方式"),
    "nav_plans": ("Plans", "方案"),
    "nav_faq": ("FAQ", "常見問題"),
    "lang_other": ("中文", "English"),
    "sign_in": ("Sign in", "登入"),
    "book_demo": ("Book a demo", "預約展示"),
    "hero_h1": ("Training that feels like play.", "訓練，宛如遊戲。"),
    "hero_lede": ("AI-guided practice for movement, speech, and cognition. Just a webcam, right in your browser.",
                  "AI 引導的動作、語言與認知練習。只需一個鏡頭，直接在瀏覽器使用。"),
    "hero_how": ("See how it works", "了解運作方式"),
    "hero_note": ("No setup fees. Cancel anytime.", "無建置費用，隨時取消。"),
    "mock_title": ("Session · Shoulder flexion", "練習中 · 肩關節屈曲"),
    "mock_feedback": ("Good form. Lift a little higher.", "姿勢正確，再抬高一點。"),
    "mock_reps": ("Reps", "次數"),
    "mock_angle": ('Range of motion (estimate)',
                   '活動範圍（估算）'),
    "mock_queue": ("Up next", "接下來"),
    "mock_q1": ("Shoulder flexion", "肩關節屈曲"),
    "mock_q2": ("Thumb to index pinch", "拇指食指捏合"),
    "mock_q3": ("Hand grasp", "手部抓握"),
    "mock_q4": ("Word repetition", "詞語複述"),
    "logos": ("Partners and press", "合作夥伴與媒體"),
    "pillars_h": ("Move. Speak. Think.", "動。說。思考。"),
    "pillars_p": ("Three kinds of daily practice in one place, each with feedback in the moment.",
                  "三種每日練習集中一處，每一次都有即時回饋。"),
    "p1_h": ("Movement", "動作練習"),
    "p1_p": ("Every motion is guided and measured, from a shoulder reach to a finger pinch.",
             "每個動作都有引導與量度，從肩膀伸展到手指捏合。"),
    "p2_h": ("Speech", "語言練習"),
    "p2_p": ("AI listens and gives instant feedback on pronunciation, in English and Cantonese.",
             "AI 聆聽並即時回饋發音，支援英語及粵語。"),
    "p3_h": ("Cognition", "認知練習"),
    "p3_p": ("Focus, memory and planning exercises that adapt their difficulty as you go.",
             "專注、記憶與規劃練習，難度隨你的表現即時調整。"),
    "who_h": ("Who it's for",
              '適合誰使用'),
    "who_p": ('Older adults, and the family and carers who help them practise at home. It does not replace your therapist or doctor.',
              '長者，以及協助他們在家練習的家人和照顧者。它不能取代你的治療師或醫生。'),
    "c_move": ('Shoulder|Elbow|Hand and wrist|Trunk|Legs|Balance',
               '肩膀|手肘|手部與手腕|軀幹|雙腿|平衡'),
    "c_speech": ('English|Cantonese|21 levels',
                 '英語|粵語|21 個級別'),
    "c_focus": ('Memory|Attention|Reaction speed',
                '記憶|專注|反應速度'),
    "w1_p": ('Exercises grouped by body region.',
             '按身體部位分類的練習。'),
    "w2_p": ('Say a word or phrase and see how close it was.',
             '說出詞語或短句，看看有多接近。'),
    "w3_h": ('Brain games',
             '腦力遊戲'),
    "w3_p": ('Short games for memory, attention and quick thinking.',
             '考驗記憶、專注和反應的短遊戲。'),
    "how_h": ("Invisible technology. Visible progress.", "看不見的科技，看得見的進步。"),
    "how_p": ('Your camera finds hand and body landmarks to count reps and estimate joint angles. These are estimates for practice, not medical measurements.',
              '鏡頭辨識手部與身體位置，用來計算次數及估算關節角度。這些只是練習用的估算，並非醫療測量。'),
    "s1_h": ("Open your browser", "打開瀏覽器"),
    "s1_p": ("Works on iPad, iPhone, Mac and PC. No sensors, nothing to install.", "支援 iPad、iPhone、Mac 及 PC，無需感測器或安裝。"),
    "s2_h": ("Pick what to work on", "選擇練習部位"),
    "s2_p": ("Choose a body region and goal. The right exercises queue up.", "選擇身體部位與目標，合適的練習自動排好。"),
    "s3_h": ("Practise with feedback", "跟著回饋練習"),
    "s3_p": ('Form tips in the moment, every rep, and a record of your progress.',
             '每一下都有即時姿勢提示，並記錄你的進度。'),
    "panel_regions": ('Body regions',
                      '身體部位'),
    "panel_exercises": ("Guided exercises", "引導練習"),
    "panel_latency": ("Feedback", "回饋"),
    "panel_latency_v": ("Real time", "即時"),
    "panel_langs": ("Languages", "語言"),
    "panel_langs_v": ("EN · 粵語", "EN · 粵語"),
    "panel_note": ('Camera video is processed on your device and is never uploaded.',
                   '鏡頭影像在你的裝置上處理，不會上載。'),
    "quotes_h": ('What practitioners and users say',
                 '治療師與用家的評價'),
    "q1": ("The games are intuitive and goal-oriented. Patients stay engaged without any hand-holding.",
           "遊戲直覺易用且目標明確，患者無需額外指導就能持續投入。"),
    "q1_who": ("Physiotherapist|Norwich City Football Club (EFL)", "物理治療師|諾域治城足球會 (EFL)"),
    "q2": ("The tutorials and objectives are crystal clear, and the platform covers a wide range of exercises.",
           "每款遊戲的教學和目標都很清晰，平台涵蓋大量練習項目。"),
    "q2_who": ("Physiotherapist|North Walsham Rugby Club", "物理治療師|北沃爾瑟姆欖球會"),
    "q4": ("Usability barriers are common for older users. The clean interface and bilingual support make this genuinely easy to use.",
           "長者常遇到使用障礙。簡潔的介面和中英雙語支援，讓整個體驗真正容易上手。"),
    "q4_who": ("Physiotherapy Student|The Hong Kong Polytechnic University", "物理治療學學生|香港理工大學"),
    "q5": ("The structured exercises fit neatly into my clients' daily home practice.", "這些結構化練習能自然融入用家的日常居家練習。"),
    "q5_who": ("Speech Therapist|Hong Kong Registered", "言語治療師|香港註冊"),
    "trust_h": ('Privacy and safety',
                '私隱與安全'),
    "trust_items": ('Camera video stays on your device|Results encrypted in transit and at rest|Delete your account in the app|Not a medical device',
                    '鏡頭影像留在你的裝置上|練習結果在傳輸及儲存時加密|可在應用程式內刪除帳戶|並非醫療器材'),
    "trust_p": ('Bonet is a practice tool. It does not diagnose or treat any condition. Ask your therapist or doctor before starting.',
                '哥基健動是練習工具，不會診斷或治療任何病況。開始之前，請先諮詢你的治療師或醫生。'),
    "trust_link": ('Privacy and safety details',
                   '私隱與安全詳情'),
    "plans_h": ('Start free.',
                '免費開始。'),
    "plans_p": ('Upgrade when you want more. Cancel anytime.',
                '想要更多時再升級，隨時取消。'),
    "plan1_h": ('Free',
                '免費'),
    "plan1_p": ('A taste of every part, every day.',
                '每日試玩每一部分。'),
    "plan1_f": ('Speaking levels 1 to 3|8 exercises|Brain games on Easy|Progress for the last 7 days',
                '說話練習第 1 至 3 級|8 個運動|腦力遊戲簡單級|最近 7 日進度'),
    "plan2_h": ('Premium',
                '完整版'),
    "plan2_p": ('HK$78 / month. 7-day free trial for new subscribers.',
                '每月 HK$78。新訂閱者可免費試用 7 日。'),
    "plan2_f": ('All 21 speaking levels|All 34 exercises and your own plans|Brain games on Medium and Hard|Progress for the whole month|Practice report to share with your therapist',
                '全部 21 級說話練習|全部 34 個運動及自訂計劃|腦力遊戲中等及困難級|整個月的進度|可與治療師分享的練習報告'),
    "get_started": ("Get started", "開始使用"),
    "faq_h": ("Questions", "常見問題"),
    "faq_g1": ("Personal", "個人"),
    "faq_g2": ('Sharing',
               '分享'),
    "faq_g3": ('Safety',
               '安全'),
    "f1q": ("Can I practise at home?", "我可以在家練習嗎？"),
    "f1a": ("Yes. It runs in any modern browser on an iPad or computer using the built-in camera. No sensors and no downloads. A computer vision model tracks your movement in real time and gives instant feedback on form and rep count.",
            "可以。它在 iPad 或電腦的瀏覽器中運作，使用內建鏡頭，無需感測器或下載。電腦視覺模型即時追蹤你的動作，並對姿勢與次數即時回饋。"),
    "f2q": ("What devices does it support?", "支援哪些裝置？"),
    "f2a": ("Any recent device with a camera: iPad, iPhone, Mac, Windows laptop, or a desktop with a USB camera. Safari, Chrome and Edge are supported. We recommend an iPad (10th generation or later) or a laptop from the last five years.",
            "任何配備鏡頭的較新裝置：iPad、iPhone、Mac、Windows 手提電腦，或接駁 USB 鏡頭的桌面電腦。支援 Safari、Chrome 及 Edge。建議使用 iPad（第 10 代或之後）或近五年內的手提電腦。"),
    "f3q": ('How long should I practise each day?',
            '每天應練習多久？'),
    "f3a": ('Sessions are short, so they fit around your day. Do what feels comfortable, rest when you are tired and stop if you feel pain. Ask your therapist or doctor how much suits you.',
            '練習時間短，方便融入日常。以自己覺得舒適為準，疲倦時休息，感到疼痛便停止。適合練習多少，請問你的治療師或醫生。'),
    "f4q": ("How is my data handled?", "我的資料如何處理？"),
    "f4a": ('Camera video is processed on your device and is never uploaded. Speech is recognised on your device where possible; otherwise it is sent to Apple (iOS app) or a cloud speech service (Cantonese on the web) to be turned into text, and we do not keep the audio. We store your account details and practice results (reps, scores, session times) in our cloud database, encrypted in transit and at rest, and each account can only read its own data. We do not use end-to-end encryption. You can delete your account and all your history in Settings.',
            '鏡頭影像在你的裝置上處理，不會上載。語音會盡量在你的裝置上辨識；否則會傳送至 Apple（iOS 應用程式）或雲端語音服務（網頁版的粵語）轉成文字，我們不會保存錄音。我們把帳戶資料和練習結果（次數、分數、時間）存放在雲端資料庫，傳輸及儲存時均有加密，而每個帳戶只能讀取自己的資料。我們沒有採用端對端加密。你可以在「設定」中刪除帳戶及全部記錄。'),
    "f5q": ('Can my therapist or family see my progress?',
            '治療師或家人可以看到我的進度嗎？'),
    "f5a": ('You can print or share a practice report from the app and give it to your therapist or family. It is a summary of the practice you did, not a clinical assessment. There are no team workspaces or clinic dashboards in the app today.',
            '你可以在應用程式內列印或分享練習報告，交給治療師或家人。報告只是你練習內容的摘要，並非臨床評估。應用程式目前沒有團隊空間或診所儀表板。'),
    "f6q": ("Is it a medical device?", "這是醫療器材嗎？"),
    "f6a": ('No. Bonet is a general wellness and practice tool. It does not diagnose, treat, cure or prevent any condition, and no medical regulator has reviewed or cleared it. Ask your therapist or doctor before you start, and stop if you feel pain or unwell.',
            '不是。哥基健動是一般健康及練習工具，不會診斷、治療、治癒或預防任何病況，亦未經任何醫療監管機構審查或批准。開始之前請先諮詢你的治療師或醫生，如感到疼痛或不適請立即停止。'),
    "cta_h": ("Daily practice, your way.", "每日練習，由你決定。"),
    "cta_p": ("See how guided practice for movement, speech and cognition fits into your day.", "了解引導式的動作、語言與認知練習如何融入你的日常。"),
    "community": ("Join the community on", "加入社群："),
    "foot_about": ('AI-guided practice for movement, speech and cognition. Made for daily use at home.',
                   'AI 引導的動作、語言與認知練習，為居家日常使用而設。'),
    "foot_product": ("Product", "產品"),
    "foot_company": ("Company", "公司"),
    "foot_resources": ("Resources", "資源"),
    "foot_about_link": ("About", "關於我們"),
    "foot_science": ("Science", "科學"),
    "foot_blog": ("Blog", "網誌"),
    "foot_terms": ("Terms", "服務條款"),
    "foot_privacy": ("Privacy", "私隱政策"),
    "foot_compliance": ('Privacy and safety',
                        '私隱與安全'),
    "rights": ("© 2026 Coglix Labs Inc.", "© 2026 Coglix Labs Inc."),
    "d_h": ("Book a demo", "預約展示"),
    "d_sub": ("Tell us a little about you and we'll get back within two working days.", "留下資料，我們會在兩個工作天內回覆。"),
    "d_name": ("Name", "姓名"),
    "d_email": ("Email", "電郵"),
    "d_org": ("Organization (optional)", "機構（選填）"),
    "d_msg": ("Message (optional)", "訊息（選填）"),
    "d_cancel": ("Cancel", "取消"),
    "d_send": ("Send request", "送出"),
    "d_sending": ("Sending…", "傳送中…"),
    "d_ok": ("Thanks. We'll be in touch soon.", "已收到，我們會盡快聯絡你。"),
    "d_err": ("That didn't go through. Please try again, or email hello@coglixlabs.com.", "未能送出，請再試一次，或電郵 hello@coglixlabs.com。"),
    "close": ("Close", "關閉"),
}

CHECK = '<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M5 10.5l3 3 7-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICONS = {
    "move": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="4.5" r="2"/><path d="M5 9l7 1.5L19 9M12 10.5V15l-3 6M12 15l3 6"/></svg>',
    "speech": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0013 0M12 17.5V21"/></svg>',
    "mind": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3a7 7 0 00-4 12.7V19h8v-3.3A7 7 0 0012 3zM9.5 21.5h5"/><path d="M12 7v4l2.5 1.5"/></svg>',
}

LOGOS = [
    ("https://www.f.inc", "img/partners/foundersinc-dark.png", "Founders, Inc."),
    ("https://daretochange.ydc.org.hk/en/showcase-coglix.aspx", "img/partners/ydc.png", "Youth Development Commission"),
    ("https://www.wenweipo.com/a/202507/24/AP68822984e4b0999ec0381875.html", "img/partners/wenweipo.png", "Wen Wei Po"),
    ("https://www.instagram.com/p/DXGoWJ9mFRo/", "img/partners/inmediahk.png", "inmediahk"),
]
QUOTE_LOGOS = {"q1": "img/norwich-city-fc.png", "q2": "img/north-walsham-rfc.png", "q4": "img/polyu.png", "q5": "img/hku.svg"}

# Upper body doing a shoulder raise, drawn as pose landmarks over the camera frame.
POSE_SVG = """<svg viewBox="0 0 640 400" aria-hidden="true">
  <defs><radialGradient id="g" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="#2f7bff" stop-opacity=".18"/><stop offset="1" stop-color="#2f7bff" stop-opacity="0"/></radialGradient></defs>
  <rect width="640" height="400" fill="url(#g)"/>
  <path d="M250 400 C250 300 262 250 320 240 C378 250 390 300 390 400Z" fill="rgba(255,255,255,.06)"/>
  <circle cx="320" cy="170" r="42" fill="rgba(255,255,255,.07)"/>
  <g stroke="#8ab8ff" stroke-width="3" stroke-linecap="round" fill="none">
    <path d="M268 250 L372 250 M268 250 L262 360 M372 250 L378 360"/>
    <path d="M268 250 L212 162 L186 72"/>
    <path d="M372 250 L420 318 L452 372"/>
  </g>
  <path d="M268 250 m-46 0 a46 46 0 0 1 14 -32" stroke="#ffffff" stroke-opacity=".6" stroke-width="2" fill="none"/>
  <g fill="#ffffff">
    <circle cx="268" cy="250" r="6"/><circle cx="372" cy="250" r="6"/><circle cx="212" cy="162" r="6"/><circle cx="186" cy="72" r="6"/>
    <circle cx="420" cy="318" r="6"/><circle cx="452" cy="372" r="6"/><circle cx="320" cy="170" r="5"/>
  </g>
  <g font-family="inherit" font-size="13" fill="#ffffff"><rect x="120" y="226" rx="10" width="78" height="26" fill="rgba(10,92,240,.85)"/><text x="133" y="244">142&#176;</text></g>
</svg>"""


def t(key, lang):
    en, zh = STRINGS[key]
    return html.escape(en if lang == "en" else zh, quote=True)


def parts(key, lang):
    return t(key, lang).split("|")


def render(lang):
    T = lambda k: t(k, lang)  # noqa: E731
    prefix = "" if lang == "en" else "../"
    other = "/zh/" if lang == "en" else "/"

    def chips(key):
        return "".join(f"<li>{c}</li>" for c in parts(key, lang))

    def feats(key):
        return "".join(f"<li>{CHECK}<span>{f}</span></li>" for f in parts(key, lang))

    logos = "".join(
        f'<li><a href="{u}" target="_blank" rel="noopener"><img src="{prefix}{src}" alt="{html.escape(alt)}" loading="lazy" height="36"></a></li>'
        for u, src, alt in LOGOS)

    quotes = []
    for q in ["q1", "q2", "q4", "q5"]:
        who, org = parts(q + "_who", lang)
        mark = (f'<img src="{prefix}{QUOTE_LOGOS[q]}" alt="" loading="lazy">' if q in QUOTE_LOGOS
                else f'<span class="initial" aria-hidden="true">{who[0]}</span>')
        quotes.append(f'<figure class="quote reveal"><blockquote>{T(q)}</blockquote>'
                      f'<figcaption>{mark}<div><strong>{who}</strong><span>{org}</span></div></figcaption></figure>')

    faq_groups = [("faq_g1", ["f1", "f2", "f3", "f4"]), ("faq_g2", ["f5"]), ("faq_g3", ["f6"])]
    faq = "".join(
        f"<h3>{T(g)}</h3>" + "".join(f"<details><summary>{T(f + 'q')}</summary><p>{T(f + 'a')}</p></details>" for f in fs)
        for g, fs in faq_groups)

    head = (DOCS / "partials" / f"head-{lang}.html").read_text()
    js_strings = {k: STRINGS[k][0 if lang == "en" else 1] for k in ["d_send", "d_sending", "d_ok", "d_err"]}
    js_strings = ",".join(f'{k}:{html.escape(repr(v), quote=False)}' for k, v in js_strings.items())

    return f"""<!DOCTYPE html>
<html lang="{'en' if lang == 'en' else 'zh-Hant'}">
<!-- Generated by scripts/build-home.py. Edit that file, not this one. -->
<head>
    <meta charset="UTF-8">
{head.rstrip()}
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <meta name="theme-color" content="#040a18">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{prefix}css/site.css">
    <script>document.documentElement.classList.add('js');</script>
</head>
<body>
<a class="skip" href="#main">{T('skip')}</a>

<header class="nav on-dark" id="nav">
    <div class="wrap nav-inner">
        <a class="brand" href="{'/' if lang == 'en' else '/zh/'}"><img src="{prefix}img/coglix-logo.jpg" alt="" width="28" height="28">{T('brand')}</a>
        <ul class="nav-links">
            <li><a href="#practice">{T('nav_practice')}</a></li>
            <li><a href="#how">{T('nav_how')}</a></li>
            <li><a href="#plans">{T('nav_plans')}</a></li>
            <li><a href="#faq">{T('nav_faq')}</a></li>
        </ul>
        <div class="nav-actions">
            <a class="text-link lang" href="{other}" hreflang="{'zh-Hant' if lang == 'en' else 'en'}">{T('lang_other')}</a>
            <a class="text-link" href="https://app.bonet.care/sign-in">{T('sign_in')}</a>
            <button class="btn btn-primary btn-sm" type="button" data-demo>{T('book_demo')}</button>
        </div>
    </div>
</header>

<main id="main">
    <section class="hero">
        <div class="wrap">
            <h1>{T('hero_h1')}</h1>
            <p class="lede">{T('hero_lede')}</p>
            <div class="hero-ctas">
                <button class="btn btn-light" type="button" data-demo>{T('book_demo')}</button>
                <a class="btn btn-outline-light" href="#how">{T('hero_how')}</a>
            </div>
            <p class="hero-note">{T('hero_note')}</p>
            <div class="mock" role="img" aria-label="{T('mock_title')}">
                <div class="mock-bar"><i></i><i></i><i></i><span>{T('mock_title')}</span></div>
                <div class="mock-body">
                    <div class="mock-cam">{POSE_SVG}<div class="mock-chip"><b></b>{T('mock_feedback')}</div></div>
                    <div class="mock-side">
                        <div class="mock-card"><small>{T('mock_reps')}</small><strong>8 / 12</strong><div class="bar"><i></i></div></div>
                        <div class="mock-card"><small>{T('mock_angle')}</small><strong>142&#176;</strong></div>
                        <div class="mock-card"><small>{T('mock_queue')}</small>
                            <ul class="mock-list"><li><span>{T('mock_q1')}</span><span>12</span></li><li><span>{T('mock_q2')}</span><span>15</span></li><li><span>{T('mock_q3')}</span><span>15</span></li><li><span>{T('mock_q4')}</span><span>10</span></li></ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section class="logos" aria-label="{T('logos')}">
        <div class="wrap">
            <p>{T('logos')}</p>
            <ul>{logos}</ul>
        </div>
    </section>

    <section class="section tint" id="practice">
        <div class="wrap">
            <div class="section-head"><h2>{T('pillars_h')}</h2><p>{T('pillars_p')}</p></div>
            <div class="grid-3">
                <article class="card reveal"><div class="icon">{ICONS['move']}</div><h3>{T('p1_h')}</h3><p>{T('p1_p')}</p></article>
                <article class="card reveal"><div class="icon">{ICONS['speech']}</div><h3>{T('p2_h')}</h3><p>{T('p2_p')}</p></article>
                <article class="card reveal"><div class="icon">{ICONS['mind']}</div><h3>{T('p3_h')}</h3><p>{T('p3_p')}</p></article>
            </div>
            <div class="section-head" style="margin-top:112px"><h2>{T('who_h')}</h2><p>{T('who_p')}</p></div>
            <div class="grid-3">
                <article class="card reveal"><h3 style="margin-top:0">{T('p1_h')}</h3><p>{T('w1_p')}</p><ul class="chips">{chips('c_move')}</ul></article>
                <article class="card reveal"><h3 style="margin-top:0">{T('p2_h')}</h3><p>{T('w2_p')}</p><ul class="chips">{chips('c_speech')}</ul></article>
                <article class="card reveal"><h3 style="margin-top:0">{T('w3_h')}</h3><p>{T('w3_p')}</p><ul class="chips">{chips('c_focus')}</ul></article>
            </div>
        </div>
    </section>

    <section class="section" id="how">
        <div class="wrap split">
            <div>
                <h2>{T('how_h')}</h2>
                <p class="lede">{T('how_p')}</p>
                <ol class="steps">
                    <li><div><strong>{T('s1_h')}</strong><span>{T('s1_p')}</span></div></li>
                    <li><div><strong>{T('s2_h')}</strong><span>{T('s2_p')}</span></div></li>
                    <li><div><strong>{T('s3_h')}</strong><span>{T('s3_p')}</span></div></li>
                </ol>
            </div>
            <div class="panel reveal">
                <dl>
                    <div><dt>{T('panel_regions')}</dt><dd>9</dd></div>
                    <div><dt>{T('panel_exercises')}</dt><dd>34</dd></div>
                    <div><dt>{T('panel_latency')}</dt><dd>{T('panel_latency_v')}</dd></div>
                    <div><dt>{T('panel_langs')}</dt><dd>{T('panel_langs_v')}</dd></div>
                </dl>
                <p>{T('panel_note')}</p>
            </div>
        </div>
    </section>

    <section class="section tint">
        <div class="wrap">
            <div class="section-head"><h2>{T('quotes_h')}</h2></div>
            <div class="quotes">{''.join(quotes)}</div>
        </div>
    </section>

    <section class="trust">
        <div class="wrap">
            <h2>{T('trust_h')}</h2>
            <ul>{chips('trust_items')}</ul>
            <p>{T('trust_p')} <a href="{prefix}compliance.html">{T('trust_link')}</a></p>
        </div>
    </section>

    <section class="section" id="plans">
        <div class="wrap">
            <div class="section-head"><h2>{T('plans_h')}</h2><p>{T('plans_p')}</p></div>
            <div class="plans">
                <article class="plan reveal"><h3>{T('plan1_h')}</h3><p>{T('plan1_p')}</p><ul>{feats('plan1_f')}</ul><a class="btn btn-ghost" href="https://app.bonet.care/sign-up">{T('get_started')}</a></article>
                <article class="plan featured reveal"><h3>{T('plan2_h')}</h3><p>{T('plan2_p')}</p><ul>{feats('plan2_f')}</ul><a class="btn btn-light" href="https://app.bonet.care/sign-up">{T('get_started')}</a></article>
            </div>
        </div>
    </section>

    <section class="section tint" id="faq">
        <div class="wrap">
            <div class="section-head"><h2>{T('faq_h')}</h2></div>
            <div class="faq">{faq}</div>
        </div>
    </section>

    <section class="section cta">
        <div class="wrap">
            <h2>{T('cta_h')}</h2>
            <p>{T('cta_p')}</p>
            <div class="hero-ctas">
                <button class="btn btn-primary" type="button" data-demo>{T('book_demo')}</button>
                <a class="btn btn-ghost" href="https://app.bonet.care/sign-in">{T('sign_in')}</a>
            </div>
            <div class="community"><span>{T('community')}</span><a href="https://discord.gg/ecb2mjR74Y" target="_blank" rel="noopener">Discord</a><a href="https://www.facebook.com/groups/1314838127150617" target="_blank" rel="noopener">Facebook</a></div>
        </div>
    </section>
</main>

<footer class="footer">
    <div class="wrap">
        <div class="footer-grid">
            <div><a class="brand" href="{'/' if lang == 'en' else '/zh/'}"><img src="{prefix}img/coglix-logo.jpg" alt="" width="28" height="28">{T('brand')}</a><p class="about">{T('foot_about')}</p></div>
            <div><h4>{T('foot_product')}</h4><ul><li><a href="#practice">{T('nav_practice')}</a></li><li><a href="#plans">{T('nav_plans')}</a></li><li><a href="https://app.bonet.care/sign-in">{T('sign_in')}</a></li></ul></div>
            <div><h4>{T('foot_company')}</h4><ul><li><a href="https://www.coglixlabs.com">{T('foot_about_link')}</a></li><li><a href="{prefix}science.html">{T('foot_science')}</a></li><li><a href="{prefix}blog/">{T('foot_blog')}</a></li></ul></div>
            <div><h4>{T('foot_resources')}</h4><ul><li><a href="{prefix}compliance.html">{T('foot_compliance')}</a></li><li><a href="{prefix}privacy.html">{T('foot_privacy')}</a></li><li><a href="{prefix}terms.html">{T('foot_terms')}</a></li></ul></div>
        </div>
        <div class="footer-base">
            <span>{T('rights')}</span>
            <nav><a href="{prefix}privacy.html">{T('foot_privacy')}</a><a href="{prefix}terms.html">{T('foot_terms')}</a><a href="{prefix}compliance.html">{T('foot_compliance')}</a><a href="https://www.linkedin.com/company/coglixlabs" target="_blank" rel="noopener">LinkedIn</a><a href="https://x.com/coglixlabs" target="_blank" rel="noopener">X</a><a href="{other}">{T('lang_other')}</a></nav>
        </div>
    </div>
</footer>

<dialog class="demo" id="demo" aria-labelledby="demo-title">
    <button class="close-x" type="button" data-close aria-label="{T('close')}">&#215;</button>
    <form id="demo-form" novalidate>
        <h2 id="demo-title">{T('d_h')}</h2>
        <p class="sub">{T('d_sub')}</p>
        <input type="hidden" name="access_key" value="687384ad-3de0-47ec-a282-47a19a73dcb5">
        <input type="hidden" name="subject" value="New demo request from bonet.care">
        <input type="checkbox" name="botcheck" class="sr-only" tabindex="-1" autocomplete="off" aria-hidden="true">
        <label>{T('d_name')}<input name="name" required autocomplete="name" maxlength="120" class="modal-input"></label>
        <label>{T('d_email')}<input name="email" type="email" required autocomplete="email" maxlength="200" class="modal-input"></label>
        <label>{T('d_org')}<input name="organization" autocomplete="organization" maxlength="200" class="modal-input"></label>
        <label>{T('d_msg')}<textarea name="message" rows="3" maxlength="2000" class="modal-input"></textarea></label>
        <p class="status" id="demo-status" role="status" aria-live="polite"></p>
        <div class="row">
            <button class="btn btn-ghost" type="button" data-close>{T('d_cancel')}</button>
            <button class="btn btn-primary" type="submit" id="demo-send">{T('d_send')}</button>
        </div>
    </form>
</dialog>

<script>
(function () {{
    var S = {{{js_strings}}};
    var dlg = document.getElementById('demo');
    var form = document.getElementById('demo-form');
    var status = document.getElementById('demo-status');
    var send = document.getElementById('demo-send');
    document.querySelectorAll('[data-demo]').forEach(function (b) {{
        b.addEventListener('click', function () {{ status.textContent = ''; status.className = 'status'; dlg.showModal(); }});
    }});
    dlg.querySelectorAll('[data-close]').forEach(function (b) {{ b.addEventListener('click', function () {{ dlg.close(); }}); }});
    dlg.addEventListener('click', function (e) {{ if (e.target === dlg) dlg.close(); }});
    form.addEventListener('submit', function (e) {{
        e.preventDefault();
        if (!form.reportValidity()) return;
        send.disabled = true; send.textContent = S.d_sending; status.textContent = ''; status.className = 'status';
        fetch('https://api.web3forms.com/submit', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json', 'Accept': 'application/json' }},
            body: JSON.stringify(Object.fromEntries(new FormData(form)))
        }}).then(function (r) {{ return r.json(); }}).then(function (d) {{
            if (!d.success) throw new Error('rejected');
            status.textContent = S.d_ok; status.className = 'status ok'; form.reset();
        }}).catch(function () {{
            status.textContent = S.d_err; status.className = 'status err';
        }}).then(function () {{ send.disabled = false; send.textContent = S.d_send; }});
    }});

    // Nav turns light once the dark hero has scrolled away
    var nav = document.getElementById('nav');
    var hero = document.querySelector('.hero');
    if ('IntersectionObserver' in window) {{
        new IntersectionObserver(function (es) {{ nav.classList.toggle('on-dark', es[0].isIntersecting); }},
            {{ rootMargin: '-60px 0px 0px 0px' }}).observe(hero);
        var io = new IntersectionObserver(function (es) {{
            es.forEach(function (x) {{ if (x.isIntersecting) {{ x.target.classList.add('in'); io.unobserve(x.target); }} }});
        }}, {{ rootMargin: '0px 0px -10% 0px' }});
        document.querySelectorAll('.reveal').forEach(function (el) {{ io.observe(el); }});
    }} else {{
        document.querySelectorAll('.reveal').forEach(function (el) {{ el.classList.add('in'); }});
    }}
}})();
</script>
</body>
</html>
"""


def main():
    for lang, out in [("en", DOCS / "index.html"), ("zh", DOCS / "zh" / "index.html")]:
        page = render(lang)
        assert not re.search(r"\{[a-z_]+\}", page.split("<script>")[0]), "unrendered placeholder"
        out.write_text(page)
        print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
