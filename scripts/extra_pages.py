"""Extra pages built by build-site.py: /what-bonet-tracks, /example-report, /android (unlinked, noindex, flagged).
build(ctx) gets the build-site module (write, head, header, footer, SITE, LANGS, ROOT). English only, site template."""
import json
import re
import parts

SITEMAP = [("/what-bonet-tracks", "0.6"), ("/example-report", "0.5")]  # /android is deliberately left out
FLAGS = {}


def _flags(root):
    f = root / "content" / "flags.json"
    return json.loads(f.read_text()) if f.exists() else {}


def _page(ctx, slug, title, desc, body, noindex=False, wide=False):
    extra = '<meta name="robots" content="noindex, nofollow">\n' if noindex else ""
    h = ctx.head("en", title, desc, f"{ctx.SITE}/{slug}", "og-en.png", app_css=False, extra=extra)
    h += ctx.header("en", inplace=set())
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc doc--legal{" doc--report" if wide else ""}">\n{body}\n</div></div></main>\n'
    h += ctx.footer("en")
    ctx.write(f"{slug}.html", h)


# ------------------------------------------------------------------ what Bonet tracks
def tracks(ctx):
    pq_on = "practice_quality" not in parts.FLAGS_OFF
    rows = [
        ("Repetitions and time", "A model on your device finds body and hand positions in the camera picture. Rules count each repetition and time the set.", "On your device", "Count and duration"),
        ("Range of movement and tracking quality", "Estimated from joint positions in a flat camera image. An estimate, not a therapist's measurement.", "On your device", "The estimate and a tracking quality number"),
        ("Speaking: words recognized, pace, pauses, score", "Speech recognition turns what you say into text. Bonet compares it with the prompt, then works out words recognized, pace and pause length.", "On your device where supported. Otherwise Apple (iPhone and iPad) or Google (web, several languages)", "The recognized text and the measures. Not the audio"),
        ("Brain games: right or wrong, tries, help used", "Simple rules pick the next item from how you did.", "On your device", "Results for each item"),
        ("Daily plan", "Fixed rules use your setup answers and recent practice to suggest what to do today.", "On your device", "Your plan and settings"),
        ("Minutes, practice days, streak", "Added up from the results above.", "Saved with your account", "Totals, streak, streak savers, points and outfit"),
        ("Weekly league points", "Points added up on our server. Some league players are computer players, and the app says so.", "Our server", "Nickname and points"),
        ("App usage events", "For example &ldquo;finished a session&rdquo;, with broad bands such as 1 to 3 minutes, tied to a random account number.", "Our analytics. They do not receive exercise results, speech text or health answers", "The event and the band"),
    ]
    tr = "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in rows)
    pq = ""
    if pq_on:
        import home
        pq = ("<!-- requires_feature: practice_quality -->\n<h2 id=\"how-it-went\">How it went</h2>\n"
              f"<p>{home.PQ['move_p'][0]}</p>\n<p>{home.PQ['speak_p'][0]}</p>\n<p>{home.PQ['caveat'][0]}</p>\n<!-- /requires_feature -->\n")
    body = f"""<div class="legal">
<h1>What Bonet tracks</h1>
<p>Every number Bonet records, how it is measured, where it is worked out and what is kept.</p>
<div class="toc"><ul><li><a href="#numbers">The numbers</a></li><li><a href="#never">What is not kept</a></li><li><a href="#limits">What the numbers are</a></li></ul></div>
<h2 id="numbers">The numbers</h2>
<table><thead><tr><th>Number</th><th>How it is measured</th><th>Where</th><th>What is kept</th></tr></thead><tbody>{tr}</tbody></table>
{pq}<h2 id="never">What is not kept</h2>
<ul>
<li>Camera video and images. They are read on your device and never recorded or uploaded.</li>
<li>Voice recordings. Bonet keeps the text and the measures, not the audio.</li>
<li>Your card number, your precise location, your contacts, photos or files.</li>
</ul>
<p>Bonet does not use your results to train models, sell them or show ads.</p>
<h2 id="limits">What the numbers are</h2>
<p>They are estimates from a camera and a microphone. They show what was practiced. They can be wrong, and a single day says little. Bonet is a practice tool, not a medical device.</p>
<p>The full detail is in <a href="/ai-and-automatic-measures">How Bonet measures</a> and the <a href="/privacy">Privacy Policy</a>. See an <a href="/example-report">example report</a>.</p>
</div>"""
    _page(ctx, "what-bonet-tracks", "What Bonet tracks | Bonet", "Every number Bonet records, how it is measured, where it is processed and what is not kept.", body)


# ------------------------------------------------------------------ example report
def report(ctx):
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
    chart = (f'<svg class="rep-chart" viewBox="0 0 {W} {H}" role="img" aria-labelledby="rc-t rc-d"><title id="rc-t">Minutes practiced each day over 14 days</title>'
             f'<desc id="rc-d">{w1} minutes in the first week and {w2} in the second. The table below has each day.</desc>{bars}</svg>')
    daytbl = "<tr>" + "".join(f"<th scope=\"col\">{i + 1}</th>" for i in range(14)) + "</tr><tr>" + "".join(f"<td>{m}</td>" for m in mins) + "</tr>"
    hexa = ""
    if pq_on:
        import math
        axes = [("Range", .8), ("Pace", .65), ("Steadiness", .7), ("Left and right", .55), ("Hold time", .75), ("Set finished", .9)]
        cx, cy, R = 130, 120, 80
        pt = lambda k, r: (cx + r * math.sin(math.pi * k / 3), cy - r * math.cos(math.pi * k / 3))
        grid = "".join('<polygon points="' + " ".join("%.1f,%.1f" % pt(k, R * f) for k in range(6)) + '" fill="none" stroke="var(--line)" stroke-width="2"/>' for f in (.5, 1))
        poly = " ".join("%.1f,%.1f" % pt(k, R * v) for k, (_, v) in enumerate(axes))
        lab = "".join('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="11" fill="var(--ink-2)">%s</text>' % (pt(k, R + 16)[0], pt(k, R + 16)[1] + 4, n) for k, (n, _) in enumerate(axes))
        hexa = (f'<!-- requires_feature: practice_quality -->\n<section class="rep-sec"><h2>How practice went: arm raise</h2>'
                f'<svg class="rep-hex" viewBox="0 0 260 240" role="img" aria-label="Example six-sided chart for one exercise: range, pace, steadiness, left and right, hold time and set finished">{grid}'
                f'<polygon points="{poly}" fill="var(--blue)" fill-opacity=".25" stroke="var(--blue)" stroke-width="3"/>{lab}</svg>'
                f'<p class="note">Automatic measures of home practice, shown as a shape for this example. Not a clinical assessment.</p></section>\n<!-- /requires_feature -->\n')
    tag = '<span class="rep-from">From the app</span>'
    body = f"""<div class="legal">
<h1>Example report</h1>
<p>This is an example of the one-page report you can print or share. All names and numbers are invented. It shows what someone practiced in Bonet. It is not a medical record or a clinical assessment. Bonet is a practice tool and does not diagnose or treat any condition.</p>
<article class="rep" aria-label="Example report, not a real person">
<p class="rep-flag"><strong>Example, not a real person.</strong> Made-up data.</p>
<header class="rep-top"><div><h2>Home practice report</h2><p>Sam Example &middot; last 14 days</p></div><img src="/img/mascot/point.webp" width="96" height="96" alt=""></header>
<dl class="rep-sum">
<div><dt>Days practiced</dt><dd>{days} of 14</dd></div>
<div><dt>Minutes</dt><dd>{total}</dd></div>
<div><dt>Current streak</dt><dd>{streak} days</dd></div>
</dl>
<section class="rep-sec"><h2>Minutes each day {tag}</h2>{chart}
<p>More minutes in the second week: {w2} against {w1}.</p>
<table class="rep-tbl"><caption class="sr">Minutes practiced on each of the 14 days</caption><thead><tr><th colspan="14" scope="colgroup">Day</th></tr></thead><tbody>{daytbl}</tbody></table></section>
<section class="rep-sec"><h2>Exercises {tag}</h2>
<table class="rep-tbl"><thead><tr><th scope="col">Exercise</th><th scope="col">Sessions</th><th scope="col">Repetitions</th></tr></thead><tbody>
<tr><th scope="row">Seated arm raise</th><td>5</td><td>60</td></tr><tr><th scope="row">Hand open and close</th><td>6</td><td>90</td></tr><tr><th scope="row">Sit to stand, with support</th><td>4</td><td>40</td></tr></tbody></table></section>
<section class="rep-sec"><h2>Speaking {tag}</h2>
<table class="rep-tbl"><thead><tr><th scope="col">Tries</th><th scope="col">Words recognized</th><th scope="col">Pace</th><th scope="col">Average pause</th></tr></thead><tbody><tr><td>9</td><td>41 of 52</td><td>84 words a minute</td><td>1.2 seconds</td></tr></tbody></table></section>
<section class="rep-sec"><h2>Brain games {tag}</h2>
<table class="rep-tbl"><thead><tr><th scope="col">Game</th><th scope="col">Plays</th><th scope="col">Items right</th></tr></thead><tbody><tr><th scope="row">Pairs</th><td>4</td><td>22 of 28</td></tr><tr><th scope="row">Memory</th><td>3</td><td>9 of 12</td></tr></tbody></table></section>
{hexa}<section class="rep-sec"><h2>Note <span class="rep-from rep-from--user">Entered by the user</span></h2><p>&ldquo;Practiced after breakfast on most days.&rdquo;</p></section>
<section class="rep-sec"><h2>Questions to bring to your therapist</h2><ul><li>Which of these exercises should I keep doing?</li><li>How often would you like me to practice?</li><li>What should I do when an exercise feels too hard?</li></ul></section>
<p class="note">These numbers are estimates from the camera and the microphone. They show what was practiced, not how someone is doing. The person decides who sees the report.</p>
<p class="rep-flag">Example, not a real person. Made-up data.</p>
</article>
<p>See <a href="/what-bonet-tracks">what Bonet tracks</a> and <a href="/ai-and-automatic-measures">how automatic measures work</a>.</p>
</div>"""
    _page(ctx, "example-report", "Example report | Bonet", "A sample one-page Bonet practice report with invented data. Not a real person.", body)


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
    tracks(ctx)
    report(ctx)
    android(ctx)
