"""Extra pages built by build-site.py: /what-bonet-tracks, /example-report, /android (unlinked, noindex, flagged).
build(ctx) gets the build-site module (write, head, header, footer, SITE, LANGS, ROOT). /what-bonet-tracks and /example-report are
built in every language: T("English", "廣東話") with strings/<lang>.json, as on the home page. /android is English only."""
import json
import re
import parts

SITEMAP = []  # /android is deliberately left out
LOCAL_SITEMAP = [("what-bonet-tracks", "0.6"), ("example-report", "0.5")]  # one entry per language, written by build-site.py
FLAGS = {}


def _flags(root):
    f = root / "content" / "flags.json"
    return json.loads(f.read_text()) if f.exists() else {}


def _page(ctx, slug, title, desc, body, noindex=False, wide=False, lang="en", local=False):
    extra = '<meta name="robots" content="noindex, nofollow">\n' if noindex else ""
    urls, alt = parts.page_urls(slug) if local else (None, None)
    pre = parts.pre(lang)
    h = ctx.head(lang, title, desc, f"{ctx.SITE}{pre}/{slug}", "og-en.png", app_css=False, extra=extra, alt=alt)
    h += ctx.header(lang, urls=urls) if local else ctx.header(lang, inplace=set())
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc doc--legal{" doc--report" if wide else ""}">\n{body}\n</div></div></main>\n'
    h += ctx.footer(lang, urls=urls)
    ctx.write(f"{pre.strip('/')}/{slug}.html".lstrip("/"), parts.localise(h, lang))


# ------------------------------------------------------------------ what Bonet tracks
def tracks(ctx, lang="en"):
    T = parts.mk(lang)
    pq_on = "practice_quality" not in parts.FLAGS_OFF
    dev = T("On your device", "喺你部機")
    rows = [
        (T("Repetitions and time", "次數同時間"), T("A model on your device finds body and hand positions in the camera picture. Rules count each repetition and time the set.", "你部機入面嘅模型喺鏡頭畫面搵出身體同手嘅位置，再按規則數每一下同計時。"), dev, T("Count and duration", "次數同時長")),
        (T("Range of movement and tracking quality", "動作幅度同追蹤質素"), T("Estimated from joint positions in a flat camera image. An estimate, not a therapist's measurement.", "由平面鏡頭畫面入面嘅關節位置估算出嚟。只係估算，唔係治療師嘅量度。"), dev, T("The estimate and a tracking quality number", "估算值同一個追蹤質素數字")),
        (T("Speaking: words recognized, pace, pauses, score", "說話：認到嘅詞語、速度、停頓、分數"), T("Speech recognition turns what you say into text. Bonet compares it with the prompt, then works out words recognized, pace and pause length.", "語音辨識將你講嘅嘢變成文字。哥基健動會同題目比較，再計出認到嘅詞語、速度同停頓長度。"), T("On your device where supported. Otherwise Apple (iPhone and iPad) or Google (web, several languages)", "部機支援嘅話就喺你部機做。否則由 Apple（iPhone 同 iPad）或者 Google（網頁版，部分語言）處理"), T("The recognized text and the measures. Not the audio", "認到嘅文字同量度結果。唔包括錄音")),
        (T("Brain games: right or wrong, tries, help used", "腦力遊戲：啱定錯、試咗幾多次、用咗幾多提示"), T("Simple rules pick the next item from how you did.", "簡單規則會按你做得點揀下一題。"), dev, T("Results for each item", "每一題嘅結果")),
        (T("Daily plan", "每日計劃"), T("Fixed rules use your setup answers and recent practice to suggest what to do today.", "固定規則會用你設定時嘅答案同最近嘅練習，建議你今日做啲乜。"), dev, T("Your plan and settings", "你嘅計劃同設定")),
        (T("Minutes, practice days, streak", "分鐘、練習日數、連續練習"), T("Added up from the results above.", "由上面嘅結果加埋。"), T("Saved with your account", "同你嘅帳戶一齊儲存"), T("Totals, streak, streak savers, points and outfit", "總數、連續練習、保護盾、分數同衣服")),
        (T("Weekly league points", "每週聯賽分數"), T("Points added up on our server. Some league players are computer players, and the app says so.", "分數喺我哋嘅伺服器加埋。聯賽入面有啲係電腦玩家，app 會講明。"), T("Our server", "我哋嘅伺服器"), T("Nickname and points", "暱稱同分數")),
        (T("App usage events", "App 使用事件"), T("For example &ldquo;finished a session&rdquo;, with broad bands such as 1 to 3 minutes, tied to a random account number.", "例如「完成咗一節練習」，只記大概範圍（例如 1 至 3 分鐘），並連住一個隨機帳戶號碼。"), T("Our analytics. They do not receive exercise results, speech text or health answers", "我哋嘅分析工具。佢哋收唔到運動結果、說話文字或者健康問題嘅答案"), T("The event and the band", "事件同範圍")),
    ]
    tr = "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in rows)
    pq = ""
    if pq_on:
        import home
        P = lambda k: T(home.PQ[k][0], home.PQ[k][1])
        pq = ("<!-- requires_feature: practice_quality -->\n<h2 id=\"how-it-went\">" + T("How it went", "做得點") + "</h2>\n"
              f"<p>{P('move_p')}</p>\n<p>{P('speak_p')}</p>\n<p>{P('caveat')}</p>\n<!-- /requires_feature -->\n")
    h1 = T("What Bonet tracks", "哥基健動記錄啲乜")
    last = T('The full detail is in <a href="/ai-and-automatic-measures">How Bonet measures</a> and the <a href="/privacy">Privacy Policy</a>. See an <a href="/example-report">example report</a>.',
             '詳情喺<a href="/ai-and-automatic-measures">哥基健動點樣量度</a>同<a href="/privacy">私隱政策</a>。亦可以睇下<a href="/example-report">示範報告</a>。')
    body = f"""<div class="legal">
<h1>{h1}</h1>
<p>{T("Every number Bonet records, how it is measured, where it is worked out and what is kept.", "哥基健動記錄嘅每一個數字：點樣量度、喺邊度計、保留啲乜。")}</p>
<div class="toc"><ul><li><a href="#numbers">{T("The numbers", "呢啲數字")}</a></li><li><a href="#never">{T("What is not kept", "唔會保留嘅嘢")}</a></li><li><a href="#limits">{T("What the numbers are", "呢啲數字代表乜")}</a></li></ul></div>
<h2 id="numbers">{T("The numbers", "呢啲數字")}</h2>
<table><thead><tr><th>{T("Number", "數字")}</th><th>{T("How it is measured", "點樣量度")}</th><th>{T("Where", "喺邊度")}</th><th>{T("What is kept", "保留啲乜")}</th></tr></thead><tbody>{tr}</tbody></table>
{pq}<h2 id="never">{T("What is not kept", "唔會保留嘅嘢")}</h2>
<ul>
<li>{T("Camera video and images. They are read on your device and never recorded or uploaded.", "鏡頭影片同圖像。只喺你部機讀取，唔會錄低或者上載。")}</li>
<li>{T("Voice recordings. Bonet keeps the text and the measures, not the audio.", "錄音。哥基健動只保留文字同量度結果，唔保留聲音。")}</li>
<li>{T("Your card number, your precise location, your contacts, photos or files.", "你嘅信用卡號碼、精確位置、通訊錄、相片或者檔案。")}</li>
</ul>
<p>{T("Bonet does not use your results to train models, sell them or show ads.", "哥基健動唔會用你嘅結果訓練模型、出售或者賣廣告。")}</p>
<h2 id="limits">{T("What the numbers are", "呢啲數字代表乜")}</h2>
<p>{T("They are estimates from a camera and a microphone. They show what was practiced. They can be wrong, and a single day says little. Bonet is a practice tool, not a medical device.", "呢啲係由鏡頭同咪高峰得出嘅估算，顯示練習咗啲乜。佢哋有可能唔準，單睇一日亦說明唔到乜。哥基健動係練習工具，唔係醫療器材。")}</p>
<p>{last}</p>
</div>"""
    _page(ctx, "what-bonet-tracks", T("What Bonet tracks | Bonet", "哥基健動記錄啲乜 | 哥基健動"), T("Every number Bonet records, how it is measured, where it is processed and what is not kept.", "哥基健動記錄嘅每一個數字：點樣量度、喺邊度處理、唔會保留啲乜。"), body, lang=lang, local=True)


# ------------------------------------------------------------------ example report
def report(ctx, lang="en"):
    T = parts.mk(lang)
    pq_on = "practice_quality" not in parts.FLAGS_OFF
    mins = [10, 0, 15, 15, 0, 10, 20, 15, 15, 0, 20, 15, 20, 25]
    days = sum(1 for m in mins if m)
    total = sum(mins)
    streak = 0
    for m in reversed(mins):
        if not m:
            break
        streak += 1
    w1, w2 = sum(mins[:7]), sum(mins[7:])
    W, H, pad, bw, gap = 560, 170, 24, 28, 12
    top = max(mins)
    bars = ""
    for i, m in enumerate(mins):
        x = pad + i * (bw + gap)
        h = round(m / top * 110)
        op = '' if m else ' opacity=".25"'
        bars += f'<rect x="{x}" y="{130 - h}" width="{bw}" height="{max(h, 2)}" rx="5" fill="var(--blue)"{op}/>'
        bars += f'<text x="{x + bw / 2}" y="150" text-anchor="middle" font-size="11" fill="var(--ink-3)">{i + 1}</text>'
    of = lambda a, b: T("{a} of {b}", "{a} / {b}").replace("{a}", str(a)).replace("{b}", str(b))
    wk = T("{w1} minutes in the first week and {w2} in the second. The table below has each day.", "第一個星期 {w1} 分鐘，第二個星期 {w2} 分鐘。下面個表有每日嘅數字。").replace("{w1}", str(w1)).replace("{w2}", str(w2))
    chart = (f'<svg class="rep-chart" viewBox="0 0 {W} {H}" role="img" aria-labelledby="rc-t rc-d"><title id="rc-t">{T("Minutes practiced each day over 14 days", "14 日入面每日練習嘅分鐘")}</title>'
             f'<desc id="rc-d">{wk}</desc>{bars}</svg>')
    daytbl = "<tr>" + "".join(f"<th scope=\"col\">{i + 1}</th>" for i in range(14)) + "</tr><tr>" + "".join(f"<td>{m}</td>" for m in mins) + "</tr>"
    hexa = ""
    if pq_on:
        import math
        axes = [(T("Range", "幅度"), .8), (T("Pace", "速度"), .65), (T("Steadiness", "穩定"), .7), (T("Left and right", "左右"), .55), (T("Hold time", "維持時間"), .75), (T("Set finished", "完成組數"), .9)]
        cx, cy, R = 130, 120, 80
        pt = lambda k, r: (cx + r * math.sin(math.pi * k / 3), cy - r * math.cos(math.pi * k / 3))
        grid = "".join('<polygon points="' + " ".join("%.1f,%.1f" % pt(k, R * f) for k in range(6)) + '" fill="none" stroke="var(--line)" stroke-width="2"/>' for f in (.5, 1))
        poly = " ".join("%.1f,%.1f" % pt(k, R * v) for k, (_, v) in enumerate(axes))
        lab = "".join('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="11" fill="var(--ink-2)">%s</text>' % (pt(k, R + 16)[0], pt(k, R + 16)[1] + 4, n) for k, (n, _) in enumerate(axes))
        hexa = (f'<!-- requires_feature: practice_quality -->\n<section class="rep-sec"><h2>{T("How practice went: arm raise", "練習做得點：舉手")}</h2>'
                f'<svg class="rep-hex" viewBox="0 0 260 240" role="img" aria-label="{T("Example six-sided chart for one exercise: range, pace, steadiness, left and right, hold time and set finished", "一個運動嘅示範六角形圖表：幅度、速度、穩定、左右、維持時間同完成組數")}">{grid}'
                f'<polygon points="{poly}" fill="var(--blue)" fill-opacity=".25" stroke="var(--blue)" stroke-width="3"/>{lab}</svg>'
                f'<p class="note">{T("Automatic measures of home practice, shown as a shape for this example. Not a clinical assessment.", "居家練習嘅自動量度，喺呢個示範入面用形狀顯示。唔係臨床評估。")}</p></section>\n<!-- /requires_feature -->\n')
    tag = f'<span class="rep-from">{T("From the app", "嚟自 app")}</span>'
    flag = T("Example, not a real person.", "示範，唔係真人。")
    made = T("Made-up data.", "資料係虛構嘅。")
    sec = "1.2" if lang not in ("es", "de", "fr") else "1,2"
    body = f"""<div class="legal">
<h1>{T("Example report", "示範報告")}</h1>
<p>{T("This is an example of the one-page report you can print or share. All names and numbers are invented. It shows what someone practiced in Bonet. It is not a medical record or a clinical assessment. Bonet is a practice tool and does not diagnose or treat any condition.", "呢個係一頁報告嘅示範，你可以列印或者分享。所有名同數字都係虛構嘅。報告顯示一個人喺哥基健動練習咗啲乜，唔係醫療紀錄，亦唔係臨床評估。哥基健動係練習工具，唔會診斷或者治療任何病況。")}</p>
<article class="rep" aria-label="{T("Example report, not a real person", "示範報告，唔係真人")}">
<p class="rep-flag"><strong>{flag}</strong> {made}</p>
<header class="rep-top"><div><h2>{T("Home practice report", "居家練習報告")}</h2><p>{T("Sam Example", "示範用戶")} &middot; {T("last 14 days", "最近 14 日")}</p></div><img src="/img/mascot/point.webp" width="96" height="96" alt=""></header>
<dl class="rep-sum">
<div><dt>{T("Days practiced", "練習日數")}</dt><dd>{of(days, 14)}</dd></div>
<div><dt>{T("Minutes", "分鐘")}</dt><dd>{total}</dd></div>
<div><dt>{T("Current streak", "目前連續練習")}</dt><dd>{T("{n} days", "{n} 日").replace("{n}", str(streak))}</dd></div>
</dl>
<section class="rep-sec"><h2>{T("Minutes each day", "每日分鐘")} {tag}</h2>{chart}
<p>{T("More minutes in the second week: {w2} against {w1}.", "第二個星期分鐘多咗：{w2} 對 {w1}。").replace("{w1}", str(w1)).replace("{w2}", str(w2))}</p>
<table class="rep-tbl"><caption class="sr">{T("Minutes practiced on each of the 14 days", "14 日入面每一日練習嘅分鐘")}</caption><thead><tr><th colspan="14" scope="colgroup">{T("Day", "日")}</th></tr></thead><tbody>{daytbl}</tbody></table></section>
<section class="rep-sec"><h2>{T("Exercises", "運動")} {tag}</h2>
<table class="rep-tbl"><thead><tr><th scope="col">{T("Exercise", "運動")}</th><th scope="col">{T("Sessions", "節數")}</th><th scope="col">{T("Repetitions", "次數")}</th></tr></thead><tbody>
<tr><th scope="row">{T("Seated arm raise", "坐住舉手")}</th><td>5</td><td>60</td></tr><tr><th scope="row">{T("Hand open and close", "手掌開合")}</th><td>6</td><td>90</td></tr><tr><th scope="row">{T("Sit to stand, with support", "扶住由坐到企")}</th><td>4</td><td>40</td></tr></tbody></table></section>
<section class="rep-sec"><h2>{T("Speaking", "說話")} {tag}</h2>
<table class="rep-tbl"><thead><tr><th scope="col">{T("Tries", "嘗試次數")}</th><th scope="col">{T("Words recognized", "認到嘅詞語")}</th><th scope="col">{T("Pace", "速度")}</th><th scope="col">{T("Average pause", "平均停頓")}</th></tr></thead><tbody><tr><td>9</td><td>{of(41, 52)}</td><td>{T("{n} words a minute", "每分鐘 {n} 個詞").replace("{n}", "84")}</td><td>{T("{n} seconds", "{n} 秒").replace("{n}", sec)}</td></tr></tbody></table></section>
<section class="rep-sec"><h2>{T("Brain games", "腦力遊戲")} {tag}</h2>
<table class="rep-tbl"><thead><tr><th scope="col">{T("Game", "遊戲")}</th><th scope="col">{T("Plays", "玩咗幾多次")}</th><th scope="col">{T("Items right", "答啱題數")}</th></tr></thead><tbody><tr><th scope="row">{T("Pairs", "配對")}</th><td>4</td><td>{of(22, 28)}</td></tr><tr><th scope="row">{T("Memory", "記憶")}</th><td>3</td><td>{of(9, 12)}</td></tr></tbody></table></section>
{hexa}<section class="rep-sec"><h2>{T("Note", "備註")} <span class="rep-from rep-from--user">{T("Entered by the user", "由用戶輸入")}</span></h2><p>{T("&ldquo;Practiced after breakfast on most days.&rdquo;", "「大部分日子都係食完早餐之後練習。」")}</p></section>
<section class="rep-sec"><h2>{T("Questions to bring to your therapist", "可以問治療師嘅問題")}</h2><ul><li>{T("Which of these exercises should I keep doing?", "呢啲運動入面，邊啲我應該繼續做？")}</li><li>{T("How often would you like me to practice?", "你想我幾耐練習一次？")}</li><li>{T("What should I do when an exercise feels too hard?", "如果覺得某個運動太難，我應該點做？")}</li></ul></section>
<p class="note">{T("These numbers are estimates from the camera and the microphone. They show what was practiced, not how someone is doing. The person decides who sees the report.", "呢啲數字係由鏡頭同咪高峰得出嘅估算，顯示練習咗啲乜，唔代表一個人嘅狀況。邊個可以睇報告，由用戶自己決定。")}</p>
<p class="rep-flag">{flag} {made}</p>
</article>
<p>{T('See <a href="/what-bonet-tracks">what Bonet tracks</a> and <a href="/ai-and-automatic-measures">how automatic measures work</a>.', '睇下<a href="/what-bonet-tracks">哥基健動記錄啲乜</a>同<a href="/ai-and-automatic-measures">自動量度點樣運作</a>。')}</p>
</div>"""
    _page(ctx, "example-report", T("Example report | Bonet", "示範報告 | 哥基健動"), T("A sample one-page Bonet practice report with invented data. Not a real person.", "哥基健動一頁練習報告嘅示範，資料係虛構嘅，唔係真人。"), body, lang=lang, local=True)


# ------------------------------------------------------------------ android early access (unlinked, noindex, flagged)
def android(ctx):
    on = bool(FLAGS.get("android_early_access", False))
    if not on:
        body = """<div class="legal"><h1>Bonet for Android</h1><p>Early access is not open yet.</p></div>"""
    else:
        langs = ["English", "繁體中文", "廣東話", "简体中文", "Español", "日本語"]
        opts = "".join(f"<option>{l}</option>" for l in langs)
        body = f"""<div class="legal">
<h1>Bonet for Android: early access</h1>
<p>Try Bonet on your Android phone or tablet before it reaches Google Play.</p>
<h2>Who this is for</h2>
<p>The Android version is new and we are still testing it. If you have an Android phone or tablet and can tell us what works and what does not, this is for you. If you would rather wait for a finished version, the Google Play release will come later and we will say so here.</p>
<h2>Sign up</h2>
<form class="android-form" data-android-form action="#" method="post" novalidate>
<label>Your name (optional)<input name="name" autocomplete="name"></label>
<label>Email<input name="email" type="email" required autocomplete="email"></label>
<label>Phone or tablet model (optional)<input name="device"></label>
<label>Language<select name="language">{opts}</select></label>
<label class="chk"><input type="checkbox" name="consent" required> Email me the download link and updates about the Android early access</label>
<input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">
<button class="btn" type="submit">Get the download</button>
<p class="note" data-android-status role="status"></p>
<p class="note">We use your email only to tell you about the Android early access. We keep it in our own database and do not share or sell it. You can ask us to delete it at any time. See the <a href="/privacy">Privacy Policy</a>.</p>
</form>
<h2>What the early-access version cannot do yet</h2>
<ul><li>Subscriptions cannot be bought in this version. While you test, Premium is switched on for your account at no cost.</li>
<li>It has been tested on emulators, not yet on many real phones. Some screens may look odd on tablets and folding phones.</li>
<li>Bonet is a practice tool, not a medical device.</li></ul>
</div>
<script defer src="/js/android.js"></script>"""
    _page(ctx, "android", "Bonet for Android: early access", "Early access registration for the Bonet Android app.", body, noindex=True)


def build(ctx):
    FLAGS.update(_flags(ctx.ROOT))
    for lang in parts.LANGS:
        tracks(ctx, lang)
        report(ctx, lang)
    android(ctx)
