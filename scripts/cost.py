"""Cost board for the home page: sliders for practice days and minutes, optional visit cost. Numbers stay in the browser (js/cost.js).
Premium price and trial length come from content/prices.json and are emitted as data attributes; nothing is hard-coded in JS."""
import re
from parts import PRICES, price_text, mk

WEEKS = 52 / 12  # a month counted as 4.33 weeks
DEFAULT = {"visits": 4, "cost": 0, "days": 3, "mins": 15}


def _num(x):
    return f"{x:.1f}".rstrip("0").rstrip(".") if x != int(x) else str(int(x))


def cost_section(lang):
    T = mk(lang)
    m = re.match(r"([^\d]*)([\d.]+)", PRICES["usd"])
    cur, amount = m.group(1), float(m.group(2))
    trial = PRICES.get("trial_days", 7)
    d = DEFAULT
    pdays = round(d["days"] * WEEKS)
    mins = pdays * d["mins"]
    per_day = amount / pdays
    between = pdays / d["visits"] if d["visits"] else None
    notset = T("Not set", "未設定")

    def slider(key, label, lo, hi, step, val, shown):
        i = f"cb-{key}"
        return (f'<div class="cb-field"><label for="{i}">{label}</label>'
                f'<output for="{i}" id="{i}-o" data-out="{key}" aria-live="polite">{shown}</output>'
                f'<input type="range" id="{i}" name="{key}" min="{lo}" max="{hi}" step="{step}" value="{val}" data-in="{key}"></div>')

    sliders = "".join([
        slider("visits", T("Therapist visits a month", "每月睇治療師次數"), 0, 12, 1, d["visits"], d["visits"]),
        slider("cost", T("What one visit costs you (US$)", "每次覆診你要俾幾多（US$）"), 0, 300, 5, d["cost"], notset),
        slider("days", T("Days a week with Bonet", "每星期用哥基健動嘅日數"), 1, 7, 1, d["days"], d["days"]),
        slider("mins", T("Minutes a day with Bonet", "每日用哥基健動嘅分鐘數"), 5, 60, 5, d["mins"], d["mins"]),
    ])

    def stat(key, label, val):
        return f'<div class="cb-stat"><dt>{label}</dt><dd><output data-out="{key}" aria-live="polite">{val}</output></dd></div>'

    stats = "".join([
        stat("pdays", T("Practice days a month", "每月練習日數"), pdays),
        stat("per_day", T("Premium cost per practice day", "完整版每個練習日嘅費用"), f"{cur}{per_day:.2f}"),
    ])
    prem_price = f'{price_text(lang)} {T("a month", "每月")}'
    free = [T("Speaking levels 1 to 3", "說話第 1 至 3 級"), T("Eight starter exercises", "八個入門運動"), T("Easy brain games", "簡單腦力遊戲")]
    prem = [T("Every level and exercise", "全部級別同運動"), T("Harder brain games", "較難嘅腦力遊戲"), T("Longer reports", "更長嘅報告")]
    rows = [
        (T("Cost", "費用"), T("Free", "免費"), f'{prem_price}<br>{T("7 days free", "免費試用 7 日")}', T("Set by your clinic", "由診所訂")),
        (T("When", "幾時"), T("Any day, at home", "喺屋企，每日都得"), T("Any day, at home", "喺屋企，每日都得"), T("At the visit", "覆診時")),
        (T("What you get", "你得到啲乜"), ", ".join(free), ", ".join(prem), T("Chosen with your therapist", "同你嘅治療師一齊揀")),
    ]
    head = ["", T("Free plan", "免費版"), T("Premium", "完整版"), T("Therapy visit", "治療覆診")]
    thead = "<tr>" + "".join(f'<th scope="col">{h}</th>' if h else '<td></td>' for h in head) + "</tr>"
    tbody = "".join(f'<tr><th scope="row">{r[0]}</th>' + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>" for r in rows)
    word = T("Count your practice days.", "數下你嘅練習日數。").split(" ")
    h2 = " ".join(word)
    return f"""<section class="sec sec--wash" id="cost"><div class="wrap">
<div class="open"><h2 class="display display--ink rv-word">{h2}</h2></div>
<div class="cb" data-cost data-cur="{cur}" data-price="{amount}" data-trial="{trial}" data-weeks="{WEEKS:.4f}" data-notset="{T('Not set', '未設定')}" data-lang="{lang}">
<form class="cb-form" aria-label="{T('Count your practice days.', '數下你嘅練習日數。')}">{sliders}</form>
<div class="cb-res">
<dl class="cb-stats">{stats}</dl>
<div class="cb-chart" data-chart>
<p class="cb-hint" data-hint>{T('Add what a visit costs you to see the bars.', '輸入每次覆診嘅費用，就睇到兩條棒。')}</p>
<div class="cb-bars" data-bars hidden>
<div class="cb-bar"><span>{T('One visit: what you pay', '一次覆診：你要俾嘅')}</span><div class="cb-track"><i data-bar="visit"></i></div><b data-val="visit"></b></div>
<div class="cb-bar cb-bar--pro"><span>{T('A month of Premium', '完整版一個月')}</span><div class="cb-track"><i data-bar="prem"></i></div><b data-val="prem">{cur}{amount}</b></div>
</div></div></div>
</div>
<p class="cb-line">{T('Bonet is for practice between visits. It does not replace your therapist.', '哥基健動係喺覆診之間練習用。佢唔會取代你嘅治療師。')}</p>
<p class="note"><a href="/compare.html#cost-sources">{T('About the numbers', '關於呢啲數字')}</a></p>
</div></section>
"""


def cost_sources():
    """English only: the sources note shown on /compare under the cost board link."""
    return """<section id="cost-sources" class="cost-sources"><h2>Sources for the cost board</h2>
<p>The cost board starts with no visit cost filled in. What a person pays per therapy visit depends on their plan, deductible, copay or coinsurance and visit limits, and we found no per-visit figure we could stand behind. Enter your own. The other outputs do not need it.</p>
<ul>
<li>Chevan J, Riddle DL, Reed M. Out-of-pocket spending for ambulatory physical therapy services from 2008 to 2012: national panel survey. <em>Physical Therapy</em>, 2015. Uses the Medical Expenditure Panel Survey (2,189 people). It reports spending per episode of care, not per visit: among people with any out-of-pocket spending the mean was $351 and the median $144, over an average of 9.9 visits. <a href="https://read.qxmd.com/read/26112257/out-of-pocket-spending-for-ambulatory-physical-therapy-services-from-2008-to-2012-national-panel-survey">Abstract</a>.</li>
<li>Skydel J, Ross J. Commercial negotiated rates for outpatient physical therapy at US hospitals. <em>JAMA Internal Medicine</em>, research letter, 2026. Median negotiated rates for evaluation services ran from $151 to $215 across hospitals. These are what insurers pay, not what patients pay. <a href="https://news.yale.edu/2026/03/05/cost-physical-therapy-varies-widely-state-state">Yale News summary</a>.</li>
</ul>
<p>We found no comparable source for speech-language therapy. A month is counted as 52 &divide; 12 weeks. Premium price and trial length come from the same file that sets the price on the home page.</p>
</section>"""
