"""Pages written for people who search by need, built by build-site.py in every language:

  /stroke-home-practice, /exercise-app-for-seniors, /speech-practice-at-home, /for-family-and-carers   (parts.NEED_PAGES)
  /compare/bonet-vs-<slug>, one per product in scripts/competitors.json                                 (parts.VS_PAGES)
  /llms.txt, a plain-text summary of the site for AI assistants (English)

Copy is T("English", "廣東話") with strings/<lang>.json, as on the home page. Numbers come from content/facts.json and
content/prices.json through {levels}, {exercises}, {free_ex}, {price}, {langs}. Every h2 of a need page is a question; the
FAQPage JSON-LD is built from those headings and the text under them, so the two cannot drift apart.
The comparison pages hold no facts of their own: every cell, note, date and link is read from competitors.json.
META holds the search titles and descriptions of older pages whose text lives elsewhere (science, therapist, faq, safety).
Rules for this copy: Bonet is a practice tool. Never say it treats, restores or improves anything."""
import json
import re
import parts
from parts import APP, FACTS, INFO_PAGES, LANG_COUNT, LANGS, MAIL, NEED_PAGES, NEED_UI, NUM_WORD, NUM_YUE, PRICES, SITE, VS_PAGES, mk, page_urls, pre, price_text, u, vs_slug
import home

LOCAL_SITEMAP = [(s, "0.8") for s in NEED_PAGES + INFO_PAGES] + [(vs_slug(s), "0.5") for s in VS_PAGES]

# Search titles and descriptions for pages whose body is a fragment: slug -> ((title en, yue), (description en, yue)).
# build-site.py uses these instead of content/pages/meta.<lang>.json and content/legal/meta.<lang>.json for these four pages.
META = {
    "science": (("How Bonet works: camera exercises, speech and brain games", "哥基健動點樣運作：鏡頭運動、說話同腦力遊戲"),
                ("How Bonet's camera-counted exercises, speaking practice and brain games work, what the app measures, and what it does not claim. Not a medical device.",
                 "哥基健動嘅鏡頭數次數運動、說話練習同腦力遊戲點樣運作，app 量度啲乜，同埋佢冇聲稱啲乜。唔係醫療器材。")),
    "therapist": (("For therapists and carers: home practice reports | Bonet", "俾治療師同照顧者：居家練習報告 | 哥基健動"),
                  ("How therapists, carers and family can see what someone practised at home in Bonet with a one-page report, how to set it up, and what the app does not do.",
                   "治療師、照顧者同家人點樣用一頁報告睇到某個人喺屋企用哥基健動練習過啲乜，點樣設定，同埋個 app 唔做啲乜。")),
    "faq": (("Bonet FAQ: safety, privacy, price and devices", "哥基健動常見問題：安全、私隱、價錢同裝置"),
            ("Short answers about Bonet, the home practice app for older adults: getting started, safety, privacy, speech and camera, price and free trial, and devices.",
             "哥基健動係為長者而設嘅居家練習 app，呢度有簡短解答：點樣開始、安全、私隱、說話同鏡頭、價錢同免費試用、裝置。")),
    "safety": (("Safety and privacy: what to know before you start | Bonet", "安全同私隱：開始之前要知嘅事 | 哥基健動"),
               ("Before you practise at home with Bonet: what it is and is not, staying safe, when to stop, emergencies and what the numbers mean. Not a medical device.",
                "喺屋企用哥基健動練習之前要知：佢係乜、唔係乜、點樣保持安全、幾時要停、緊急情況，同埋啲數字代表乜。唔係醫療器材。")),
}


def meta(slug, lang):
    """(title, description) of one of the META pages in this language."""
    T = mk(lang)
    (t_en, t_yue), (d_en, d_yue) = META[slug]
    return T(t_en, t_yue), T(d_en, d_yue)


def _fill(s, lang):
    return (s.replace("{levels}", str(FACTS["speaking_levels"])).replace("{exercises}", str(FACTS["exercises"])).replace("{free_ex}", str(FACTS["free_exercises"]))
             .replace("{price}", price_text(lang)).replace("{langs}", str(LANG_COUNT)))


def _ld(x):
    return f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False).replace("</", "<" + chr(92) + "/")}</script>\n'


def _plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).replace(" .", ".").replace(" ,", ",").strip()


def _crumbs(lang, trail):
    """BreadcrumbList: trail = [(name, path)], paths without the language prefix."""
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": n + 1, "name": name, "item": f"{SITE}{pre(lang)}{path}"} for n, (name, path) in enumerate(trail)]}


DISCLAIMER = ("Bonet is a practice tool. It is not a medical device and does not diagnose or treat. Ask your doctor or therapist what practice is right for you.",
              "哥基健動係練習工具，唔係醫療器材，亦唔會診斷或者治療。邊啲練習啱你，請問你嘅醫生或者治療師。")
COST = ("p", "You can start free. The free plan includes {free_ex} of the {exercises} exercises, speaking levels 1 to 3 and brain games on Easy. Premium is {price} a month, with 7 days free, and you can cancel any time.",
        "你可以免費開始。免費版包括 {exercises} 個運動入面嘅 {free_ex} 個、說話第 1 至 3 級，同埋簡單級嘅腦力遊戲。完整版每月 {price}，可以免費試用 7 日，隨時可以取消。")
LANG_LINE = (f"{NUM_WORD[LANG_COUNT]} languages: English, Chinese, Japanese, Spanish, German and French.", f"{NUM_YUE[LANG_COUNT]}種語言：英文、中文、日文、西班牙文、德文同法文。")
DEMO_ALT = {
    "hero": ("Animated preview: tap Start on the Today path, the camera counts three arm raises, Great set, and the step is ticked.", "動畫預覽：喺「今日」路徑撳開始，鏡頭數三下舉手，完成一組，然後打咗剔。"),
    "move": ("Animated preview of the exercise screen counting 1, 2, 3 reps beside a 3D guide.", "動畫預覽：運動畫面一邊有立體示範，一邊數 1、2、3 下。"),
    "speak": ("Animated preview: word tiles move into place to build a sentence and Great! appears.", "動畫預覽：詞語磚砌成句子，然後出現「好呀！」。"),
    "progress": ("Animated preview: a weekly progress chart drawing in.", "動畫預覽：每週進度圖表逐條畫出。"),
}

# Each page: title, description, h1, the plain answer shown first, the demo and the section it follows, then the sections.
# A section is (question, [blocks]); a block is ("p", en, yue), ("ul", [(en, yue)]) or ("ol", [(en, yue)]).
PAGES = {
    "stroke-home-practice": {
        "title": ("Home practice after a stroke: a daily practice app | Bonet", "中風後喺屋企練習：每日練習 app | 哥基健動"),
        "desc": ("A daily practice app for people practising at home after a stroke: camera-counted exercises, speaking practice with hints and brain games. Not a medical device.",
                 "每日練習 app，啱中風後喺屋企練習嘅人用：鏡頭數次數嘅運動、有提示嘅說話練習同腦力遊戲。唔係醫療器材。"),
        "h1": ("Daily home practice after a stroke", "中風後喺屋企每日練習"),
        "answer": ("Bonet is an app for daily practice at home, used by older adults and by people practising after a stroke. It puts movement exercises counted by your camera, speaking practice with hints and short brain games into one daily plan. It is a practice tool, not a medical device, and it does not replace your therapist.",
                   "哥基健動係一個喺屋企每日練習用嘅 app，長者同中風後練習嘅人都用得。佢將鏡頭幫你數次數嘅運動、有提示嘅說話練習同簡短腦力遊戲，放埋喺一個每日計劃入面。佢係練習工具，唔係醫療器材，亦唔會取代你嘅治療師。"),
        "demo": ("hero", 0),
        "sections": [
            (("What can I practise at home after a stroke with Bonet?", "中風後喺屋企，我可以用哥基健動練習啲乜？"), [
                ("p", "One daily plan covers three kinds of practice. You choose what to do and how much.", "一個每日計劃包埋三種練習。做啲乜、做幾多，由你決定。"),
                ("ul", [
                    ("Movement: {exercises} exercises for shoulders and arms, hands, sit-to-stand, legs and balance. A 3D guide shows the move and your camera counts each repetition.",
                     "運動：{exercises} 個運動，包括肩膀同手臂、手部、坐到站、雙腿同平衡。立體示範教你點做，鏡頭幫你數每一下。"),
                    ("Speaking: say words, name pictures, build sentences and listen. If you get stuck, hints grow one step at a time.",
                     "說話：講詞語、認圖片、砌句子、聽說話。唔識講嘅話，提示會一步一步加大。"),
                    ("Thinking: six short games for memory, attention and quick thinking. The difficulty follows how you do.",
                     "腦力：六款簡短遊戲，練習記憶、專注同反應。難度會跟你做得點而調整。"),
                ]),
            ]),
            (("What does Bonet do, and what does it not do?", "哥基健動會做啲乜，唔會做啲乜？"), [
                ("p", "What it does:", "佢會做嘅事："),
                ("ul", [
                    ("It counts repetitions, times each set and gives a short tip after a session.", "數次數、為每一組計時，練習完俾你一個簡短提示。"),
                    ("In speaking practice it shows the words it recognised, your pace and your pauses.", "說話練習入面，顯示佢認到嘅詞語、你嘅速度同停頓。"),
                    ("It keeps a record of the days and minutes you practised, and a one-page report you can print or share.", "記低你練習咗邊幾日、幾多分鐘，仲有一頁報告俾你列印或者分享。"),
                ]),
                ("p", "What it does not do:", "佢唔會做嘅事："),
                ("ul", [
                    ("It does not diagnose, treat, cure or prevent any condition.", "唔會診斷、治療、治癒或者預防任何病況。"),
                    ("It does not replace your doctor, therapist or speech-language pathologist.", "唔會取代你嘅醫生、治療師或者言語治療師。"),
                    ("It has not been tested in a clinical trial, and no regulator has reviewed or cleared it.", "未經臨床試驗，亦冇任何監管機構審查或者批准過。"),
                    ("Its numbers are estimates from a camera and a microphone. They can be wrong.", "啲數字係由鏡頭同咪高峰得出嘅估算，有可能唔準。"),
                ]),
            ]),
            (("How do I start?", "我點樣開始？"), [
                ("ol", [
                    ("Ask your doctor or therapist first, and show them the exercises you plan to do.", "先問你嘅醫生或者治療師，俾佢哋睇下你打算做嘅運動。"),
                    ("Open <a href=\"https://app.bonet.care/\">app.bonet.care</a> in a browser on a phone, tablet or computer with a camera and a microphone.", "用有鏡頭同咪高峰嘅手機、平板或者電腦，喺瀏覽器打開 <a href=\"https://app.bonet.care/\">app.bonet.care</a>。"),
                    ("Answer a few setup questions. Bonet suggests a short plan for today.", "答幾條設定問題，哥基健動就會建議今日嘅簡短計劃。"),
                    ("Sit in a stable chair, or stand next to something sturdy you can hold, and begin with a few minutes.", "坐喺一張穩陣嘅凳，或者企喺可以扶住嘅穩固物件旁邊，由幾分鐘開始。"),
                ]),
                ("p", "The free plan is enough to try all three kinds of practice. Premium is {price} a month, with 7 days free.", "免費版已經夠你試晒三種練習。完整版每月 {price}，可以免費試用 7 日。"),
            ]),
            (("When should I ask my therapist?", "幾時應該問治療師？"), [
                ("ul", [
                    ("Before you start, and whenever the app and your therapist say different things. Do what your therapist says.", "開始之前要問；app 同治療師講法唔同嘅時候都要問。跟治療師講嘅做。"),
                    ("If an exercise hurts, feels too hard, or you are not sure it is safe for you.", "如果某個運動會痛、覺得太難，或者你唔肯定對你安唔安全。"),
                    ("If you want to know what your numbers mean. Bonet shows what you practised, not how you are doing.", "如果你想知啲數字代表乜。哥基健動顯示你練習咗啲乜，唔代表你嘅狀況。"),
                ]),
                ("p", "Stop if you feel pain, dizziness or unwell. If you notice sudden face drooping, weakness or trouble speaking, call your local emergency number right away. Bonet cannot call for help.",
                 "覺得痛、頭暈或者唔舒服就要停。如果突然面部下垂、無力或者講嘢有困難，請即刻打當地緊急電話。哥基健動唔可以幫你求救。"),
            ]),
            (("Can I share my practice with my therapist or family?", "我可唔可以俾治療師或者家人睇我嘅練習？"), [
                ("p", "Yes. Bonet makes a one-page report of the days, minutes and exercises you practised. You print it or share it yourself; Bonet does not send it to anyone. It is a summary of home practice, not a medical record or a clinical assessment. See an <a href=\"/example-report\">example report</a>.",
                 "可以。哥基健動會將你練習嘅日數、分鐘同運動整成一頁報告。報告由你自己列印或者分享，哥基健動唔會幫你傳俾任何人。佢係居家練習嘅摘要，唔係醫療紀錄，亦唔係臨床評估。可以睇下<a href=\"/example-report\">示範報告</a>。"),
            ]),
        ],
    },
    "exercise-app-for-seniors": {
        "title": ("Exercise app for seniors: gentle home exercises | Bonet", "長者運動 app：喺屋企做輕鬆運動 | 哥基健動"),
        "desc": ("An exercise app for seniors: gentle home exercises your camera counts, seated options, big text and a Simple mode. Free to start. Not a medical device.",
                 "為長者而設嘅運動 app：喺屋企做輕鬆運動，鏡頭幫你數次數，有坐住做嘅選擇、大字同簡單模式。免費開始。唔係醫療器材。"),
        "h1": ("Exercise app for seniors: gentle exercises at home", "長者運動 app：喺屋企做輕鬆運動"),
        "answer": ("Bonet is a home exercise app made with older adults in mind. A 3D guide shows each gentle exercise, your camera counts the repetitions on your device, and several exercises are done seated. Big text and a Simple mode keep the screen calm. It is a practice tool, not a medical device.",
                   "哥基健動係為長者而設嘅居家運動 app。立體示範教你做每個輕鬆運動，鏡頭喺你部機幫你數次數，有幾個運動係坐住做嘅。大字同簡單模式令畫面清晰易睇。佢係練習工具，唔係醫療器材。"),
        "demo": ("move", 1),
        "sections": [
            (("What exercises are in the app?", "App 入面有啲乜運動？"), [
                ("p", "There are {exercises} exercises, grouped by part of the body. The free plan includes {free_ex} of them.", "一共有 {exercises} 個運動，按身體部位分組。免費版包括其中 {free_ex} 個。"),
                ("ul", [
                    ("Shoulders and arms", "肩膀同手臂"),
                    ("Hands and wrists", "手部同手腕"),
                    ("Neck, back and trunk", "頸、背同軀幹"),
                    ("Legs, sit-to-stand and balance", "雙腿、坐到站同平衡"),
                ]),
            ]),
            (("How does the camera count my exercises?", "鏡頭點樣幫我數運動次數？"), [
                ("p", "Put your phone, tablet or computer where the camera can see you. A model on your device finds body and hand positions in the picture, and simple rules count each repetition and time the set. After a set you get a short tip, for example about height, steadiness, or left and right.",
                 "將手機、平板或者電腦放喺鏡頭影到你嘅位置。你部機入面嘅模型會喺畫面搵出身體同手嘅位置，再按簡單規則數每一下同計時。做完一組會有個簡短提示，例如關於幅度、穩定或者左右。"),
                ("ul", [
                    ("Camera video is read on your device. It is never recorded or uploaded.", "鏡頭影像只喺你部機讀取，唔會錄低或者上載。"),
                    ("The count is an estimate. Light, camera angle and loose clothing can change it.", "次數只係估算。光線、鏡頭角度同鬆身衫都會影響佢。"),
                    ("Do not rely on the camera to keep you safe. It can miss a loss of balance.", "唔好靠鏡頭保障安全。佢可能留意唔到你失平衡。"),
                ]),
            ]),
            (("Can I exercise sitting down?", "我可唔可以坐住做運動？"), [
                ("p", "Yes. Several exercises are done seated, such as seated knee extension and seated trunk rotation, and you can skip, shorten or repeat any exercise. If balance is a concern, practise seated, or stand next to a wall or a sturdy table and have someone nearby.",
                 "可以。有幾個運動係坐住做嘅，例如坐姿伸腿同坐姿軀幹旋轉；任何運動你都可以跳過、縮短或者重複。如果擔心平衡，可以坐住練習，或者企喺牆邊或穩固嘅枱旁邊，並且搵人喺附近陪住。"),
            ]),
            (("Is it easy to use for older adults?", "長者用起嚟容唔容易？"), [
                ("ul", [
                    ("Big text: a large-text option makes everything easier to read.", "大字：開咗大字選項，所有嘢都易睇啲。"),
                    ("Simple mode: one big Start button instead of a busy screen.", "簡單模式：一個大大嘅開始掣，取代密密麻麻嘅畫面。"),
                    ("One daily plan, so you do not have to choose from a long list.", "一個每日計劃，唔使喺長長嘅清單入面揀。"),
                    ("{langs} languages, including English, Chinese, Japanese, Spanish, German and French.", "{langs} 種語言，包括英文、中文、日文、西班牙文、德文同法文。"),
                    ("A corgi coach named Bonet, a streak and a weekly league, if you like a little encouragement.", "如果你想有啲鼓勵，仲有柯基教練朱古力、連續練習同每週聯賽。"),
                ]),
            ]),
            (("What does it cost?", "要幾多錢？"), [COST]),
            (("Is it safe for me to start?", "我開始練習安唔安全？"), [
                ("p", "Ask your doctor or therapist first, especially if you have had a stroke, a heart problem, a recent fall or balance problems. Start slow, use a clear space with good light, and stop if you feel pain, dizziness or unwell. Read <a href=\"/safety\">what to know before you start</a>.",
                 "請先問你嘅醫生或者治療師，尤其係你曾經中風、有心臟問題、最近跌過或者有平衡問題。慢慢開始，搵個光線充足、冇雜物嘅地方，覺得痛、頭暈或者唔舒服就要停。請睇<a href=\"/safety\">開始之前要知嘅事</a>。"),
            ]),
        ],
    },
    "speech-practice-at-home": {
        "title": ("Speech practice at home: daily speaking practice app | Bonet", "喺屋企練習說話：每日說話練習 app | 哥基健動"),
        "desc": ("Speaking practice at home: say words, name pictures and build sentences, with hints when you get stuck. {levels} levels per type, {langs} languages. Not speech therapy.",
                 "喺屋企練習說話：講詞語、認圖片、砌句子，唔識講有提示。每種練習有 {levels} 級，支援 {langs} 種語言。唔係言語治療。"),
        "h1": ("Speech practice at home, with hints when you get stuck", "喺屋企練習說話，唔識講有提示"),
        "answer": ("Bonet lets you practise speaking at home, a few minutes a day. You say words, name pictures, build sentences and listen. When you get stuck, hints grow one step at a time. Each practice type has {levels} levels, in {langs} languages. It is a practice tool, not speech therapy, and does not diagnose or treat.",
                   "哥基健動俾你喺屋企練習說話，每日幾分鐘。你可以講詞語、認圖片、砌句子同聽說話。唔識講嘅時候，提示會一步一步加大。每種練習有 {levels} 級，支援 {langs} 種語言。佢係練習工具，唔係言語治療，亦唔會診斷或者治療。"),
        "demo": ("speak", 0),
        "sections": [
            (("What kinds of speaking practice are there?", "有邊幾種說話練習？"), [
                ("ul", [
                    ("Say words and phrases aloud.", "大聲講出詞語同短句。"),
                    ("Name pictures.", "認圖片，講出名稱。"),
                    ("Build sentences.", "砌句子。"),
                    ("Listen.", "聽說話。"),
                ]),
                ("p", "Each type has {levels} levels, so you can begin where it feels comfortable and move up slowly. Items you found hard come back later for review.",
                 "每種練習有 {levels} 級，你可以由覺得舒服嘅級別開始，慢慢升上去。未熟嘅題目之後會再出現俾你複習。"),
            ]),
            (("What happens when I cannot find the word?", "講唔出個字嘅時候會點？"), [
                ("p", "You get a hint. Hints grow one step at a time, so you get just enough help to keep going. Using hints is part of practice, not a mistake.",
                 "你會有提示。提示一步一步加大，俾你啱啱夠嘅幫助繼續落去。用提示係練習嘅一部分，唔係做錯。"),
            ]),
            (("What does Bonet measure when I speak?", "我講嘢嘅時候，哥基健動量度啲乜？"), [
                ("p", "Speech recognition turns what you say into text. Bonet compares the text with the prompt and works out:", "語音辨識將你講嘅嘢變成文字。哥基健動會同題目比較，再計出："),
                ("ul", [
                    ("the words it recognised;", "認到嘅詞語；"),
                    ("your pace;", "你嘅速度；"),
                    ("the length of your pauses;", "停頓嘅長度；"),
                    ("a score for the try.", "今次嘗試嘅分數。"),
                ]),
                ("p", "Recognition runs on your device where the device supports it. Otherwise it is handled by Apple (on iPhone and iPad) or Google (on the web, for several languages). Bonet keeps the recognised text and the measures. It does not keep voice recordings. See <a href=\"/what-bonet-tracks\">what Bonet tracks</a>.",
                 "部機支援嘅話，辨識會喺你部機進行。否則由 Apple（iPhone 同 iPad）或者 Google（網頁版，部分語言）處理。哥基健動只保留認到嘅文字同量度結果，唔保留錄音。詳情請睇<a href=\"/what-bonet-tracks\">哥基健動記錄啲乜</a>。"),
            ]),
            (("Why did it miss words I said well?", "點解我講得好好，佢都聽漏？"), [
                ("p", "Speech recognition is less accurate with some accents, quiet or slow speech, background noise, and speech changed by a stroke. A low score may be the app's mistake, not yours. Move closer to the microphone, find a quiet place, or use the hints.",
                 "遇到某啲口音、細聲或者慢慢講、背景嘈吵，或者中風後有改變嘅說話，語音辨識會冇咁準。分數低可能係個 app 錯，唔係你錯。可以行近啲咪高峰、搵個靜啲嘅地方，或者用提示。"),
            ]),
            (("Which languages can I practise in?", "可以用邊啲語言練習？"), [("p",) + LANG_LINE]),
            (("Is this speech therapy?", "呢個係唔係言語治療？"), [
                ("p", "No. Bonet is practice you do yourself, for example between visits. It does not assess your speech or replace a speech-language pathologist. Ask your therapist which practice suits you and how often to do it. You can bring the one-page report to your next visit.",
                 "唔係。哥基健動係你自己做嘅練習，例如喺覆診之間做。佢唔會評估你嘅說話能力，亦唔會取代言語治療師。邊種練習啱你、幾耐做一次，請問你嘅治療師。你可以帶埋一頁報告去下次覆診。"),
                ("p", "The free plan includes speaking levels 1 to 3. Premium opens all {levels} levels for {price} a month, with 7 days free.", "免費版包括說話第 1 至 3 級。完整版每月 {price}，開放全部 {levels} 級，可以免費試用 7 日。"),
            ]),
        ],
    },
    "for-family-and-carers": {
        "title": ("For family and carers: set up home practice | Bonet", "俾家人同照顧者：幫手設定居家練習 | 哥基健動"),
        "desc": ("How a family member or carer sets up Bonet for someone practising at home, what the one-page report shows, and what is shared. Not a medical device.",
                 "家人或者照顧者點樣幫喺屋企練習嘅人設定哥基健動、一頁報告有啲乜，同埋會分享啲乜。唔係醫療器材。"),
        "h1": ("For family and carers: helping someone practise at home", "俾家人同照顧者：幫人喺屋企練習"),
        "answer": ("A family member or carer can set Bonet up for someone else, with that person's agreement. Bonet then suggests a short daily plan of movement, speaking and brain games, and keeps a one-page report the person can print or share. Nothing is sent to you automatically. It is a practice tool, not a medical device.",
                   "只要對方同意，家人或者照顧者可以幫佢設定哥基健動。之後哥基健動會建議一個簡短嘅每日計劃，有運動、說話同腦力遊戲，仲會整一頁報告，俾用戶自己列印或者分享。冇任何嘢會自動傳俾你。佢係練習工具，唔係醫療器材。"),
        "demo": ("progress", 1),
        "sections": [
            (("How do I set Bonet up for someone else?", "我點樣幫人設定哥基健動？"), [
                ("ol", [
                    ("Make sure the person agrees to use Bonet and has checked with their doctor or therapist.", "確保對方同意用哥基健動，並且已經問過佢嘅醫生或者治療師。"),
                    ("Open <a href=\"https://app.bonet.care/\">app.bonet.care</a> on their phone, tablet or computer. When the app asks who will use it, say you are setting it up for someone else.", "喺佢部手機、平板或者電腦打開 <a href=\"https://app.bonet.care/\">app.bonet.care</a>。App 問邊個會用嘅時候，揀你係幫人設定。"),
                    ("Answer the setup questions together. Turn on Simple mode and large text if a calmer screen helps.", "一齊答設定問題。如果簡潔啲嘅畫面有幫助，可以開簡單模式同大字。"),
                    ("Clear a safe space with good light and a stable chair, and stay near for balance exercises.", "預備一個光線充足、冇雜物嘅安全空間同一張穩陣嘅凳；做平衡運動嘅時候留喺附近。"),
                ]),
            ]),
            (("What is in the one-page report?", "一頁報告入面有啲乜？"), [
                ("ul", [
                    ("The days practised, the minutes and the current streak.", "練習日數、分鐘同目前連續練習嘅日數。"),
                    ("The exercises done, with sessions and repetitions.", "做過嘅運動，連節數同次數。"),
                    ("Speaking: tries, words recognised, pace and pauses.", "說話：嘗試次數、認到嘅詞語、速度同停頓。"),
                    ("Brain games played and items right.", "玩過嘅腦力遊戲同答啱嘅題數。"),
                    ("A note the person can add, and questions to bring to the therapist.", "用戶可以加嘅備註，同埋可以問治療師嘅問題。"),
                ]),
                ("p", "The free plan covers the last two weeks; Premium covers longer ranges. The report shows what was practised. It is not a medical record or a clinical assessment. See an <a href=\"/example-report\">example report</a>.",
                 "免費版涵蓋最近兩星期；完整版可以睇更長嘅時間。報告顯示練習咗啲乜，唔係醫療紀錄，亦唔係臨床評估。可以睇下<a href=\"/example-report\">示範報告</a>。"),
            ]),
            (("What is shared, and with whom?", "會分享啲乜，同邊個分享？"), [
                ("ul", [
                    ("The report is shared only when the person prints it or shares it. Bonet does not send it to family or therapists.", "報告只會喺用戶自己列印或者分享嘅時候先俾人睇到。哥基健動唔會將佢傳俾家人或者治療師。"),
                    ("Camera video is analysed on the device and never recorded or uploaded. Voice recordings are not kept.", "鏡頭影像只喺部機分析，唔會錄低或者上載。亦唔會保留錄音。"),
                    ("Other players in the weekly league see only a nickname and points.", "每週聯賽嘅其他玩家只睇到暱稱同分數。"),
                    ("Bonet does not sell data or show ads.", "哥基健動唔會出售資料，亦唔會賣廣告。"),
                ]),
                ("p", "The full detail is in the <a href=\"/privacy\">Privacy Policy</a>.", "詳情喺<a href=\"/privacy\">私隱政策</a>。"),
            ]),
            (("What should I watch for as a carer?", "作為照顧者，我要留意啲乜？"), [
                ("p", "You know the person best. Stop the session if they seem unwell, in pain or dizzy, and call your local emergency number for sudden face drooping, weakness or trouble speaking. Bonet does not watch over anyone and cannot call for help.",
                 "你最了解對方。如果佢睇落唔舒服、痛或者頭暈，就停止練習；如果突然面部下垂、無力或者講嘢有困難，請打當地緊急電話。哥基健動唔會睇住任何人，亦唔可以幫手求救。"),
            ]),
            (("Can I see their results from my own phone?", "我可唔可以喺自己部手機睇到佢嘅結果？"), [
                ("p", "Not today. There are no dashboards, remote monitoring or alerts in the app. The report is the way to look at practice together, and it can start a conversation with the therapist.",
                 "暫時唔可以。App 而家冇儀表板、遠程監測或者警示。報告就係一齊睇練習情況嘅方法，亦可以用嚟同治療師打開話題。"),
            ]),
            (("What does it cost?", "要幾多錢？"), [COST]),
        ],
    },
}


import info_pages  # noqa: E402  the fact pages: /about, /camera-rep-counting, /pricing
PAGES.update({k: dict(v, sections=[(q, [COST if b == "COST" else b for b in blocks]) for q, blocks in v["sections"]]) for k, v in info_pages.PAGES.items()})


def _block(b, T, lang):
    if b[0] == "p":
        return f"<p>{_fill(T(b[1], b[2]), lang)}</p>"
    return f"<{b[0]}>" + "".join(f"<li>{_fill(T(en, yue), lang)}</li>" for en, yue in b[1]) + f"</{b[0]}>"


def _more(T, lang, skip=None):
    """Links every landing page ends with: the other need pages, then FAQ, safety, example report and the comparison."""
    links = [(f"/{p}", u(NEED_UI[p], lang)) for p in NEED_PAGES if p != skip]
    links.insert(0, ("/practice", u("f_library", lang)))
    links[1:1] = [(f"/{p}", u(NEED_UI[p], lang)) for p in INFO_PAGES if p != skip]
    links += [("/faq", T("Frequently asked questions", "常見問題")), ("/safety", T("What to know before you start", "開始之前要知嘅事")),
              ("/example-report", T("Example report", "示範報告")), ("/compare", T("How Bonet compares", "同其他方案比較"))]
    return f'<p><strong>{T("More about Bonet", "更多關於哥基健動")}</strong></p>\n<ul>' + "".join(f'<li><a href="{h}">{x}</a></li>' for h, x in links) + "</ul>"


def _write(ctx, lang, slug, title, desc, body, ld, demos=False):
    urls, alt = page_urls(slug)
    h = ctx.head(lang, title, desc, alt[lang], "og-en.png", app_css=demos, extra="".join(_ld(x) for x in ld), alt=alt)
    h += ctx.header(lang, urls=urls)
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc doc--legal">\n<div class="legal">\n{body}\n</div>\n</div></div></main>\n'
    h += ctx.footer(lang, urls=urls, demos=demos)
    ctx.write(f"{pre(lang).strip('/')}/{slug}.html".lstrip("/"), parts.localise(h, lang))


def need_page(ctx, slug, lang):
    T = mk(lang)
    p = PAGES[slug]
    tx = lambda k: _fill(T(*p[k]), lang)
    start = f'<p><a class="btn btn--lg" href="{APP}/">{u("start", lang)}</a></p>'
    demo_name, demo_after = p["demo"] or (None, -1)
    fig = "" if not demo_name else (f'<figure><div class="card-demo" data-ss-fill><div class="demo" data-demo="{demo_name}"{" data-pq=" + chr(34) + "1" + chr(34) if demo_name == "hero" and "practice_quality" not in parts.FLAGS_OFF else ""}'
           f' role="img" aria-label="{parts.esc(T(*DEMO_ALT[demo_name]))}"></div></div></figure>')
    body = f'<h1>{tx("h1")}</h1>\n<div class="alert"><p>{tx("answer")}</p></div>\n{start}\n'
    faq = []
    for n, ((q_en, q_yue), blocks) in enumerate(p["sections"]):
        q = T(q_en, q_yue)
        inner = "\n".join(_block(b, T, lang) for b in blocks)
        body += f'<h2 id="q{n + 1}">{q}</h2>\n{inner}\n'
        if n == demo_after:
            body += fig + "\n"
        faq.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _plain(inner)}})
    body += f'{start}\n{_more(T, lang, slug)}\n<p class="note">{T(*DISCLAIMER)}</p>'
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq},
          _crumbs(lang, [("Bonet", "/"), (u(NEED_UI[slug], lang), f"/{slug}")])]
    _write(ctx, lang, slug, tx("title"), tx("desc"), body, ld, demos=bool(demo_name))


# ------------------------------------------------------------------ Bonet next to one other product: every fact comes from competitors.json
CMP = home.CMP
VS_NAMES = {v: k for k, v in VS_PAGES.items()}
DATE = ("13 November 2026", "2026 年 11 月 13 日")  # CMP["fetchedOn"], written out; the build stops if the file moves on without this line
assert CMP["fetchedOn"] == "2026-11-13" and CMP["asOf"] == "November 2026", "competitors.json has a new date: update DATE and the as-of strings in seo_pages.py and home.py"


def vs_links(lang, skip=None):
    T = mk(lang)
    return [(f"/{vs_slug(s)}", T("Bonet vs {name}", "哥基健動同 {name} 比較").replace("{name}", n)) for s, n in VS_PAGES.items() if s != skip]


def vs_page(ctx, slug, lang):
    T = mk(lang)
    name = VS_PAGES[slug]
    idx = CMP["columns"].index(name)
    N = lambda en, yue: _fill(T(en, yue), lang).replace("{name}", name)
    pq_on = "practice_quality" not in parts.FLAGS_OFF
    rows = list(CMP["rows"])
    if pq_on:
        PQ = home.PQ
        rows.insert(4, {"key": "quality", "cells": {c: {"v": v[0], "note": v[1], "yue": v[2]} for c, v in PQ["row_cells"].items()}})
    src_word = T("Source", "來源")
    tr, unchecked, sources = "", [], []
    for r in rows:
        k = r["key"]
        if k == "quality":
            lab, bv, bn = T(*home.PQ["row_label"][:2]), "yes", T(*home.PQ["row_bonet"][:2])
        else:
            lab, bv, bn = T(home.ENLAB[k], home.ZHLAB[k]), home.BONET[k][0][0], T(home.BONET[k][0][1], home.BONET[k][1][1])
        cell = r["cells"][name]
        v = cell["v"]
        note = T(cell["note"], cell.get("yue") or home.ZHN.get(cell["note"], cell["note"]))
        src = cell.get("src", "")
        link = f' <a href="{src}">{src_word}</a>' if src.startswith("http") else ""
        if src.startswith("http") and src not in sources:
            sources.append(src)
        if v == "unverified":
            unchecked.append(f"<li>{lab}: {note}</li>")
        tr += (f'<tr><th scope="row">{lab}</th><td><strong>{T(home.ENV[bv], home.ZHV[bv])}</strong><br>{bn}</td>'
               f'<td><strong>{T(home.ENV[v], home.ZHV[v])}</strong><br>{note}{link}</td></tr>')
    first = name.split()[0] if name != "Lingraphica TalkPath" else "TalkPath"
    better_src = [b["src"] for b in CMP["othersDoBetter"] if b["text"].startswith(first)]
    for s in better_src:
        if s not in sources:
            sources.append(s)
    better_links = ", ".join(f'<a href="{s}">{re.sub(r"^https?://(www[.])?", "", s).rstrip("/")}</a>' for s in dict.fromkeys(better_src))
    q1 = N("How do Bonet and {name} compare, feature by feature?", "哥基健動同 {name} 逐項比較係點？")
    q2 = N("What does {name} do better than Bonet?", "{name} 有邊啲地方做得好過哥基健動？")
    q3 = N("What could we not check about {name}?", "關於 {name}，有啲乜我哋核實唔到？")
    q4 = N("Where do these facts come from?", "呢啲資料係邊度嚟？")
    q5 = N("What is Bonet?", "哥基健動係乜？")
    intro = N("Bonet is a daily home practice app for movement, speaking and brain games. This page sets it beside {name}, using only what {name}'s own public pages said as of November 2026. Where a page did not say, we wrote \"not offered, as far as we can tell\" or \"not checked\" instead of guessing. We are not connected to {name}.",
              "哥基健動係每日居家練習 app，有運動、說話同腦力遊戲。呢一頁將佢同 {name} 放埋一齊比較，只用 {name} 自己嘅公開頁面截至 2026 年 11 月所講嘅內容。頁面冇講明嘅地方，我哋寫「據我哋所知冇提供」或者「未核實」，唔會估。我哋同 {name} 冇任何關係。")
    prices = N("Prices are what each company's own page showed on {date}. What each price includes differs.", "價錢係各公司自己頁面喺 {date} 顯示嘅價錢。每個價錢包含嘅內容都唔同。").replace("{date}", T(*DATE))
    if unchecked:
        un = f'<p>{N("These rows could not be confirmed from the pages we read, so they are marked as not checked:", "以下項目喺我哋睇過嘅頁面核實唔到，所以標示為未核實：")}</p>\n<ul>{"".join(unchecked)}</ul>'
    else:
        un = f'<p>{N("Every row in the table could be read from the pages listed below. Where a detail was missing, the note in that row says so.", "表入面每一項都可以喺下面列出嘅頁面睇到。有細節冇講明嘅地方，嗰一項嘅附註有寫明。")}</p>'
    trial = T("Bonet has not been tested in a clinical trial and is not a medical device. How long each company has been in the market was not stated on the pages we read, so we make no claim about it.", "哥基健動未經臨床試驗，亦唔係醫療器材。各公司入市幾耐，我哋睇過嘅頁面冇講明，所以唔作比較。")
    about = N("Bonet is a smaller home practice app with fewer exercises: {exercises} movement exercises counted by your camera, speaking practice with {levels} levels per practice type, and six brain games, in one daily plan. It is free to start. Premium is {price} a month, with 7 days free.",
              "哥基健動係較細嘅居家練習 app，練習數量較少：{exercises} 個由鏡頭數次數嘅運動、每種練習有 {levels} 級嘅說話練習，同六款腦力遊戲，全部喺一個每日計劃入面。可以免費開始。完整版每月 {price}，可以免費試用 7 日。")
    more = [("/compare", T("The full comparison table", "完整比較表"))] + vs_links(lang, slug) + [(f"/{p}", u(NEED_UI[p], lang)) for p in NEED_PAGES] + [("/faq", T("Frequently asked questions", "常見問題")), ("/safety", T("What to know before you start", "開始之前要知嘅事"))]
    b_i = home.BETTER[idx]
    body = f"""<h1>{N("Bonet vs {name}", "哥基健動同 {name} 比較")}</h1>
<div class="alert"><p>{intro}</p></div>
<h2 id="table">{q1}</h2>
<table class="vs"><thead><tr><th scope="col">{T('Feature', '項目')}</th><th scope="col">Bonet</th><th scope="col">{name}</th></tr></thead><tbody>{tr}</tbody></table>
<p class="note">{prices}</p>
<h2 id="better">{q2}</h2>
<p>{T(b_i[0], b_i[1])}</p>
<p class="note">{src_word}: {better_links}</p>
<h2 id="not-checked">{q3}</h2>
{un}
<p>{trial}</p>
<h2 id="sources">{q4}</h2>
<p>{N("From {name}'s own public pages, read on {date}:", "嚟自 {name} 自己嘅公開頁面，於 {date} 讀取：").replace("{date}", T(*DATE))}</p>
<ul>{"".join(f'<li><a href="{s}">{s}</a></li>' for s in sources)}</ul>
<h2 id="bonet">{q5}</h2>
<p>{about}</p>
<p><a class="btn btn--lg" href="{APP}/">{u("start", lang)}</a></p>
<p><strong>{T("More about Bonet", "更多關於哥基健動")}</strong></p>
<ul>{"".join(f'<li><a href="{h}">{x}</a></li>' for h, x in more)}</ul>
<p class="note">{T(*DISCLAIMER)}</p>"""
    title = N("Bonet vs {name}: features, price and sources", "哥基健動同 {name} 比較：功能、價錢同來源")
    desc = N("Bonet and {name} compared feature by feature, from {name}'s own pages as of November 2026: practice types, languages and price, with sources.",
             "哥基健動同 {name} 逐項比較，資料嚟自 {name} 自己嘅頁面（截至 2026 年 11 月）：練習種類、語言同價錢，附資料來源。")
    ld = [_crumbs(lang, [("Bonet", "/"), (T("How Bonet compares", "同其他方案比較"), "/compare"), (N("Bonet vs {name}", "哥基健動同 {name} 比較"), f"/{vs_slug(slug)}")])]
    _write(ctx, lang, vs_slug(slug), title, desc, body, ld)


# ------------------------------------------------------------------ /llms.txt
def llms(ctx):
    """Plain markdown for AI assistants (https://llmstxt.org). English, facts from content/facts.json and content/prices.json."""
    import practice_pages  # here, not at the top: practice_pages imports this module
    f, usd, trial = FACTS, PRICES["usd"], PRICES.get("trial_days", 7)
    names = ", ".join(f"{d['name']} ({SITE}{d['path']})" for d in LANGS.values())
    need = {"stroke-home-practice": "Daily practice at home after a stroke: what Bonet does and does not do, how to start, when to ask the therapist.",
            "exercise-app-for-seniors": "Gentle camera-counted exercises for older adults, seated options, big text and Simple mode.",
            "speech-practice-at-home": f"Speaking practice with hints, {f['speaking_levels']} levels per practice type, and what is measured.",
            "for-family-and-carers": "How a family member or carer sets Bonet up, the one-page report, and what is shared."}
    L = lambda path, name, note: f"- [{name}]({SITE}{path}): {note}"
    text = f"""# Bonet

> Bonet is a daily home practice app for older adults, including people practising at home after a stroke. One daily plan combines movement exercises counted by the device camera, speaking practice with hints, and short brain games. Bonet is a practice tool, not a medical device.

Bonet (Chinese name: 哥基健動) is made by Coglix Labs Inc. The web app is at {APP}/ and this site, {SITE}/, describes it. The mascot and coach is a corgi named Bonet.

## Facts

- What it is: an app for daily practice at home. Move: {f['exercises']} exercises with a 3D guide, repetitions counted by the camera on the device. Speak: say words, name pictures, build sentences and listen, with hints that grow one step at a time and {f['speaking_levels']} levels per practice type. Think: six short brain games for memory, attention and quick thinking.
- Who it is for: older adults keeping active, people practising at home after a stroke or injury, people practising between physiotherapy or speech therapy visits, and the family members and carers who help them.
- What it is not: Bonet is not a medical device and not a therapy. It does not diagnose, treat, cure or prevent any condition, and it does not replace a doctor, therapist or speech-language pathologist. It has not been tested in a clinical trial and no regulator has reviewed or cleared it. Its numbers are estimates and can be wrong. Bonet is a different app from Bold and is not connected to it.
- Price: a free plan ({f['free_exercises']} of {f['exercises']} exercises, speaking levels 1 to 3 of {f['speaking_levels']}, brain games on Easy). Premium is {usd} a month with {trial} days free for new subscribers; cancel any time.
- Languages ({len(LANGS)}): {names}.
- Where it runs: in a modern web browser at {APP}/ on a phone, tablet or computer with a camera and a microphone.
- Privacy: camera video is analysed on the device and is never recorded or uploaded. Voice recordings are not kept. No ads and no sale of data.
- Report: a one-page practice report the person can print or share with a therapist or family. Bonet does not send it to anyone. It is not a medical record or a clinical assessment.
- Reviews and studies: none are published. Please do not attribute ratings, user counts, outcomes or clinical evidence to Bonet.
- Contact: {MAIL}

## Pages by need

{chr(10).join(L("/" + s, parts.UI[NEED_UI[s]]["en"], need[s]) for s in NEED_PAGES)}

## Practice library

Generated from the app's own data: names, instructions and levels are the app's wording. Pages describe the movement and the practice only; none says an exercise is for a condition.

{practice_pages.llms_section()}

## About the app

{L("/", "Home", "What you practise, plans and price, short comparison table.")}
{L("/about", "About Bonet", "Plain facts: what Bonet is and is not, who makes it, price, languages, privacy. Bonet is not the app Bold.")}
{L("/camera-rep-counting", "Camera rep counting", "How the device camera counts repetitions, what is kept, and how accurate it is.")}
{L("/pricing", "Pricing", "The free plan and Premium, what each includes, and the free trial.")}
{L("/science", "How Bonet works", "How the camera, speaking and brain practice work, what is measured, and what is not claimed.")}
{L("/what-bonet-tracks", "What Bonet tracks", "Every number recorded, how it is measured, where, and what is never kept.")}
{L("/example-report", "Example report", "A sample one-page practice report with invented data.")}
{L("/therapist", "For therapists and carers", "How to see what someone practised, and what the app does not do.")}
{L("/faq", "Frequently asked questions", "Getting started, safety, privacy, speech and camera, plans and billing, devices.")}
{L("/safety", "What to know before you start", "Safety notices, when to stop, emergencies, what the numbers mean.")}

## Comparisons

Facts about other products come only from each company's own public pages as of {CMP['asOf']}, with sources and with what the other product does better.

{L("/compare", "How Bonet compares", "The full table with notes and sources.")}
{chr(10).join(L("/" + vs_slug(s), f"Bonet vs {n}", f"Bonet beside {n}, feature by feature.") for s, n in VS_PAGES.items())}

## Policies

{L("/privacy", "Privacy Policy", "What is collected, what stays on the device, who receives data, how to delete an account.")}
{L("/terms", "Terms of Service", "The terms for using Bonet.")}
{L("/subscriptions", "Subscriptions and refunds", "Free trial, renewal, cancelling, refunds.")}
{L("/ai-and-automatic-measures", "How Bonet measures", "How the automatic measures work and their limits.")}

## Other languages

Every page above exists in each language under its prefix: {", ".join(d["path"] for c, d in LANGS.items() if c != "en")}. For example {SITE}/ja/faq and {SITE}/es/stroke-home-practice.
"""
    ctx.write("llms.txt", text)


def build(ctx):
    for lang in LANGS:
        for slug in NEED_PAGES + INFO_PAGES:
            need_page(ctx, slug, lang)
        for slug in VS_PAGES:
            vs_page(ctx, slug, lang)
    llms(ctx)
