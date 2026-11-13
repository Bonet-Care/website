"""Cost board for the home page: sliders for practice days and minutes, optional visit cost. Numbers stay in the browser (js/cost.js).
Premium price and trial length come from content/prices.json and are emitted as data attributes; nothing is hard-coded in JS."""
import re
from parts import PRICES, price_text, mk

WEEKS = 52 / 12  # a month counted as 4.33 weeks
DEFAULT = {"cost": 0, "days": 3, "mins": 10, "ther": "some"}


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
    notset = T("Not set", "未設定")

    def slider(key, label, lo, hi, step, val, shown, extra="", attr=""):
        i = f"cb-{key}"
        return (f'<div class="cb-field"{attr}><label for="{i}">{label}</label>'
                f'<output for="{i}" id="{i}-o" data-out="{key}" aria-live="polite">{shown}</output>'
                f'<input type="range" id="{i}" name="{key}" min="{lo}" max="{hi}" step="{step}" value="{val}" data-in="{key}" style="--p:{(val - lo) / (hi - lo) * 100:.1f}%">{extra}</div>')

    opts = [("none", T("Not now", "暫時冇")), ("some", T("Now and then", "間中")), ("month", T("About monthly", "大約每月一次")), ("often", T("Every week or two", "每一至兩星期"))]
    choice = (f'<fieldset class="cb-choice"><legend>{T("Do you see a therapist?", "你有冇睇治療師？")}</legend><div class="cb-opts">'
              + "".join(f'<label><input type="radio" name="ther" value="{v}" data-ther{" checked" if v == d["ther"] else ""}><span>{t}</span></label>' for v, t in opts)
              + '</div></fieldset>')
    tip = f'<p class="cb-tip" data-tip>{T("Add a visit cost to compare.", "輸入覆診費用就可以比較。")}</p>'
    form = "".join([
        slider("days", T("Days a week with Bonet", "每星期用哥基健動嘅日數"), 1, 7, 1, d["days"], d["days"]),
        slider("mins", T("Minutes a day with Bonet", "每日用哥基健動嘅分鐘數"), 5, 60, 5, d["mins"], d["mins"]),
        choice,
        slider("cost", T("What one visit costs you (US$)", "每次覆診你要俾幾多（US$）"), 0, 300, 5, d["cost"], notset, tip, " data-costfield"),
    ])

    def stat(key, label, val, cls=""):
        return f'<div class="cb-stat {cls}"><dt>{label}</dt><dd><output data-out="{key}" aria-live="polite">{val}</output></dd></div>'

    stats = "".join([
        stat("pdays", T("Practice days a month", "每月練習日數"), pdays, "cb-stat--main"),
        stat("mins_month", T("Minutes with Bonet a month", "每月用哥基健動嘅分鐘"), mins),
        stat("per_day", T("Everyday price per practice day", "每個練習日嘅日常價錢"), f"{cur}{per_day:.2f}"),
    ])
    cells = "".join('<i></i>' for _ in range(30))
    h2 = T("Count your practice days.", "數下你嘅練習日數。")
    msg_none = T("No visits planned? Bonet still gives you a plan, feedback and a record every day.", "暫時冇覆診？哥基健動每日照樣俾你計劃、回饋同紀錄。")
    msg_n = T("Between visits you would have {n} guided practice days on record.", "兩次覆診之間，你會有 {n} 個有指引嘅練習日紀錄。")
    return f"""<section class="sec sec--wash" id="cost"><div class="wrap">
<div class="open open--c"><h2 class="display display--ink rv-word">{h2}</h2></div>
<div class="cb" data-cost data-cur="{cur}" data-price="{amount}" data-trial="{trial}" data-weeks="{WEEKS:.4f}" data-notset="{T('Not set', '未設定')}" data-lang="{lang}" data-msg-none="{msg_none}" data-msg-n="{msg_n}">
<form class="cb-form cb-card" aria-label="{h2}">{form}</form>
<div class="cb-res cb-card">
<div class="cb-cal"><div><p class="cb-cap">{T('Your month', '你嘅一個月')}</p><div class="cb-days" data-days role="img" aria-label="{T('Practice days this month', '今個月嘅練習日')}">{cells}</div></div>
<img class="cb-pup" data-pup src="/img/mascot/encourage.webp" width="512" height="512" alt=""></div>
<dl class="cb-stats">{stats}</dl>
<p class="cb-msg" data-msg aria-live="polite"></p>
<div class="cb-bars" data-bars hidden>
<div class="cb-bar"><span>{T('One visit: what you pay', '一次覆診：你要俾嘅')}</span><div class="cb-track"><i data-bar="visit"></i></div><b data-val="visit"></b></div>
<div class="cb-bar cb-bar--pro"><span>{T('A month of Premium', '完整版一個月')}</span><div class="cb-track"><i data-bar="prem"></i></div><b data-val="prem">{cur}{amount}</b></div>
</div>
</div>
</div>
<p class="cb-line">{T('Bonet is for practice between visits. It does not replace your therapist.', '哥基健動係喺覆診之間練習用。佢唔會取代你嘅治療師。')}</p>
<p class="note cb-note"><a href="/compare.html#cost-sources">{T('About the numbers', '關於呢啲數字')}</a></p>
</div></section>
"""


def cost_sources(lang="en"):
    """The sources note shown on /compare under the cost board link. Citations stay as published; the prose is translated."""
    T = mk(lang)
    c1 = T("Uses the Medical Expenditure Panel Survey (2,189 people). It reports spending per episode of care, not per visit: among people with any out-of-pocket spending the mean was $351 and the median $144, over an average of 9.9 visits.",
           "用咗 Medical Expenditure Panel Survey（2,189 人）嘅數據。佢報告嘅係每個護理療程嘅支出，唔係每次覆診：喺有自付支出嘅人入面，平均數係 $351，中位數係 $144，平均覆診 9.9 次。")
    c2 = T("Median negotiated rates for evaluation services ran from $151 to $215 across hospitals. These are what insurers pay, not what patients pay.",
           "各醫院評估服務嘅協議收費中位數由 $151 至 $215。呢啲係保險公司俾嘅錢，唔係病人俾嘅錢。")
    return f"""<section id="cost-sources" class="cost-sources"><h2>{T("Sources for the cost board", "費用計算板嘅資料來源")}</h2>
<p>{T("The cost board starts with no visit cost filled in. What a person pays per therapy visit depends on their plan, deductible, copay or coinsurance and visit limits, and we found no per-visit figure we could stand behind. Enter your own. The other outputs do not need it.", "費用計算板一開始冇填覆診費用。每次見治療師要俾幾多，視乎各人嘅保險計劃、自付額、定額或者按比例分擔，同埋覆診次數上限；我哋搵唔到一個企得住腳嘅每次費用數字。請輸入你自己嘅數字。其他結果唔需要用到佢。")}</p>
<ul>
<li>Chevan J, Riddle DL, Reed M. Out-of-pocket spending for ambulatory physical therapy services from 2008 to 2012: national panel survey. <em>Physical Therapy</em>, 2015. {c1} <a href="https://read.qxmd.com/read/26112257/out-of-pocket-spending-for-ambulatory-physical-therapy-services-from-2008-to-2012-national-panel-survey">{T("Abstract", "摘要")}</a>.</li>
<li>Skydel J, Ross J. Commercial negotiated rates for outpatient physical therapy at US hospitals. <em>JAMA Internal Medicine</em>, research letter, 2026. {c2} <a href="https://news.yale.edu/2026/03/05/cost-physical-therapy-varies-widely-state-state">{T("Yale News summary", "Yale News 摘要")}</a>.</li>
</ul>
<p>{T("We found no comparable source for speech-language therapy. A month is counted as 52 &divide; 12 weeks. Premium price and trial length come from the same file that sets the price on the home page.", "言語治療方面，我哋搵唔到可以比較嘅來源。一個月當 52 &divide; 12 個星期計。完整版價錢同試用期長度，同主頁價錢用同一個檔案。")}</p>
</section>"""
