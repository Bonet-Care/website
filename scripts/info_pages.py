"""Fact pages built by seo_pages.py in every language, with the same schema as seo_pages.PAGES:
  /about                plain facts about Bonet (also the place that says Bonet is not the app Bold)
  /camera-rep-counting  how the camera counts repetitions, kept consistent with the practice library wording
  /home-exercise-tracking       how home practice is recorded and shared with a therapist or family
  /movement-speech-brain-games  the three kinds of practice in one daily plan
  /pricing              the two plans, read from content/prices.json and content/facts.json through placeholders
Copy is (English, Cantonese); the other languages come from strings/<lang>.json. "COST" stands for seo_pages.COST.
Rules: Bonet is a practice tool. Never say it treats, restores or improves anything. No em dashes or arrows."""

# The plan lists on the home page (scripts/home.py), checked there against the app's limits; same strings, so the same translations.
HOME_FREE = [("Speaking levels 1 to 3 of {levels}", "說話第 1 至 3 級（共 {levels} 級）"), ("{free_ex} of {exercises} exercises", "{exercises} 個運動揀 {free_ex} 個"), ("Brain games on Easy", "腦力遊戲簡單級"),
             ("Last 7 days of progress", "最近 7 日嘅進度"), ("Report for the last 2 weeks", "最近 2 星期嘅報告"), ("Streak, league, outfits", "連續練習、聯賽、換衫")]
HOME_PREM = [("All {levels} speaking levels", "全部 {levels} 級說話練習"), ("All {exercises} exercises, your own plans", "全部 {exercises} 個運動，仲可以自訂計劃"), ("Every brain game level", "所有腦力遊戲級別"),
             ("Full history and report", "完整歷史同報告"), ("Everything in Free", "免費版嘅全部功能")]

LANG_NAMES = ("English, Cantonese, Traditional Chinese, Simplified Chinese, Japanese, Spanish, German and French",
              "英文、廣東話、繁體中文、簡體中文、日文、西班牙文、德文同法文")

# A1: hero sub line on the home page (replaces 'Daily practice for older adults, including after a stroke.')
HERO_SUB = ("Bonet is a daily home practice app for older adults, including people practising after a stroke.",
            "哥基健動係為長者而設嘅每日居家練習 app，中風後練習嘅人都用得。")
# A1: one more FAQ item (content/pages/faq.<lang>.html)
FAQ_LANG = (("Which languages is Bonet in?", "哥基健動有邊幾種語言？"),
            ("Eight: English, Cantonese, Traditional Chinese, Simplified Chinese, Japanese, Spanish, German and French. The app, the speaking practice and this site are in all eight. Some speech recognition needs an internet connection.",
             "八種：英文、廣東話、繁體中文、簡體中文、日文、西班牙文、德文同法文。App、說話練習同呢個網站都有齊八種語言。有啲語音辨識需要連網。"))

PAGES = {
    # ---------------------------------------------------------------- A2
    "about": {
        "title": ("About Bonet: what it is, who makes it, key facts", "關於哥基健動：係乜、邊個整、重要資料"),
        "desc": ("Key facts about Bonet, the daily home practice app for older adults made by Coglix Labs Inc.: what it includes, price, languages, privacy, and what it is not.",
                 "哥基健動嘅重要資料：Coglix Labs Inc. 為長者而設嘅每日居家練習 app，包括乜、價錢、語言、私隱，同埋佢唔係乜。"),
        "h1": ("About Bonet", "關於哥基健動"),
        "answer": ("Bonet (Chinese name 哥基健動) is a daily home practice app for older adults, including people practising at home after a stroke. It is made by Coglix Labs Inc. and runs in a web browser at app.bonet.care. It is a practice tool, not a medical device.",
                   "哥基健動（英文名 Bonet）係為長者而設嘅每日居家練習 app，中風後喺屋企練習嘅人都用得。佢由 Coglix Labs Inc. 開發，喺瀏覽器打開 app.bonet.care 就用得。佢係練習工具，唔係醫療器材。"),
        "demo": ("hero", 0),
        "sections": [
            (("What does Bonet include?", "哥基健動包括啲乜？"), [
                ("ul", [
                    ("Move: {exercises} exercises with a 3D guide. The camera on your device counts each repetition.", "運動：{exercises} 個運動，有立體示範。你部機嘅鏡頭幫你數每一下。"),
                    ("Speak: say words, name pictures, build sentences and listen, with hints that grow one step at a time. {levels} levels per practice type.", "說話：講詞語、認圖片、砌句子、聽說話，提示會一步一步加大。每種練習有 {levels} 級。"),
                    ("Think: six short brain games for memory, attention and quick thinking.", "腦力：六款簡短遊戲，練習記憶、專注同反應。"),
                    ("A one-page practice report you can print or share with a therapist or family.", "一頁練習報告，可以列印或者俾治療師、家人睇。"),
                    ("A corgi coach named Bonet.", "柯基教練朱古力。"),
                ]),
            ]),
            (("Who is Bonet for?", "哥基健動啱邊個用？"), [
                ("ul", [
                    ("Older adults who want to keep active at home.", "想喺屋企保持活躍嘅長者。"),
                    ("People practising at home after a stroke or an injury.", "中風或者受傷之後喺屋企練習嘅人。"),
                    ("People practising between physiotherapy or speech therapy visits.", "喺物理治療或者言語治療覆診之間練習嘅人。"),
                    ("Family members and carers who help them.", "幫手嘅家人同照顧者。"),
                ]),
            ]),
            (("What is Bonet not?", "哥基健動唔係乜？"), [
                ("ul", [
                    ("It is not a medical device and not a therapy. It does not diagnose, treat, cure or prevent any condition.", "佢唔係醫療器材，亦唔係治療。佢唔會診斷、治療、治癒或者預防任何病況。"),
                    ("It does not replace a doctor, therapist or speech-language pathologist.", "佢唔會取代醫生、治療師或者言語治療師。"),
                    ("It has not been tested in a clinical trial, and no regulator has reviewed or cleared it.", "未經臨床試驗，亦冇任何監管機構審查或者批准過。"),
                    ("Its numbers are estimates from a camera and a microphone. They can be wrong.", "啲數字係由鏡頭同咪高峰得出嘅估算，有可能唔準。"),
                    ("It is a different app from Bold and is not connected to it.", "佢同 Bold 係兩個唔同嘅 app，彼此冇關係。"),
                ]),
            ]),
            (("How much does it cost?", "要幾多錢？"), ["COST", ("p", "See <a href=\"/pricing\">pricing</a> for what each plan includes.", "每個方案包括啲乜，可以睇<a href=\"/pricing\">價錢</a>。")]),
            (("Which languages is it in?", "有邊幾種語言？"), [
                ("p", "Eight: English, Cantonese, Traditional Chinese, Simplified Chinese, Japanese, Spanish, German and French.", "八種：英文、廣東話、繁體中文、簡體中文、日文、西班牙文、德文同法文。"),
            ]),
            (("What happens to my camera video and voice?", "我嘅鏡頭影像同聲音會點處理？"), [
                ("ul", [
                    ("Camera video is analysed on your device. It is never recorded or uploaded.", "鏡頭影像只喺你部機分析，唔會錄低或者上載。"),
                    ("Voice recordings are not kept.", "錄音唔會保留。"),
                    ("There are no ads, and your data is not sold.", "冇廣告，亦唔會出賣你嘅資料。"),
                ]),
                ("p", "Read the <a href=\"/privacy\">privacy policy</a> and <a href=\"/what-bonet-tracks\">what Bonet tracks</a>.", "請睇<a href=\"/privacy\">私隱政策</a>同<a href=\"/what-bonet-tracks\">哥基健動記錄啲乜</a>。"),
            ]),
            (("Are there studies or reviews of Bonet?", "有冇關於哥基健動嘅研究或者評價？"), [
                ("p", "Not yet. No studies of Bonet have been published, and we do not show ratings or user numbers.", "暫時未有。未有任何關於哥基健動嘅研究發表，我哋亦唔會顯示評分或者用戶數字。"),
            ]),
            (("Who makes Bonet, and how do I contact you?", "邊個整哥基健動？點樣聯絡你哋？"), [
                ("p", "Bonet is made by Coglix Labs Inc. Email <a href=\"mailto:hello@coglixlabs.com\">hello@coglixlabs.com</a>.", "哥基健動由 Coglix Labs Inc. 開發。請電郵 <a href=\"mailto:hello@coglixlabs.com\">hello@coglixlabs.com</a>。"),
                ("p", "<a href=\"https://coglixlabs.com/\">Coglix Labs</a> was co-founded by <a href=\"https://haileycheng.com/\">Hailey Cheng</a>, a student at Columbia University.",
                 "<a href=\"https://coglixlabs.com/\">Coglix Labs</a> 嘅聯合創辦人係 <a href=\"https://haileycheng.com/\">Hailey Cheng（鄭曦琳）</a>，佢喺哥倫比亞大學讀書。"),
            ]),
        ],
    },
    # ---------------------------------------------------------------- A3
    "camera-rep-counting": {
        "title": ("Camera rep counting for home exercise | Bonet", "鏡頭數運動次數：喺屋企做運動 | 哥基健動"),
        "desc": ("How Bonet counts exercise repetitions with your device camera: how it works, what it measures, why video stays on your device, and its limits. Not a medical device.",
                 "哥基健動點樣用你部機嘅鏡頭數運動次數：點運作、量度啲乜、點解影像只留喺你部機，同埋有咩限制。唔係醫療器材。"),
        "h1": ("Exercise repetitions counted by your camera, at home", "喺屋企做運動，鏡頭幫你數次數"),
        "answer": ("Bonet uses the camera on your phone, tablet or computer to count exercise repetitions while you practise at home. A model on your device finds body and hand positions, and simple rules count each repetition and time the set. Video is never recorded or uploaded. The count is an estimate, and Bonet is a practice tool, not a medical device.",
                   "哥基健動用你手機、平板或者電腦嘅鏡頭，喺你屋企練習時幫你數運動次數。你部機入面嘅模型會搵出身體同手嘅位置，再按簡單規則數每一下同為每組計時。影像唔會錄低或者上載。次數只係估算，哥基健動係練習工具，唔係醫療器材。"),
        "demo": ("move", 0),
        "sections": [
            (("How does camera rep counting work?", "鏡頭數次數係點運作？"), [
                ("ol", [
                    ("Put your device where the camera can see you, in a clear space with good light.", "將部機放喺鏡頭影到你嘅位置，揀個光線充足、冇雜物嘅地方。"),
                    ("A 3D guide shows the exercise.", "立體示範教你點做。"),
                    ("As you move, a model on your device finds body and hand positions in each picture.", "你郁嘅時候，你部機入面嘅模型會喺每個畫面搵出身體同手嘅位置。"),
                    ("Simple rules count each repetition and time the set.", "再按簡單規則數每一下，同為每組計時。"),
                    ("A repetition is counted when you reach the position, hold it for about one second, and then come back to the start. The next repetition begins after you have returned.",
                     "你去到個姿勢，保持大約一秒，再返回起點，就算一下。你返回之後，先會開始下一下。"),
                    ("After the set you get a short tip, for example about height, steadiness, or left and right.", "做完一組會有個簡短提示，例如關於幅度、穩定或者左右。"),
                ]),
            ]),
            (("What does it measure?", "佢量度啲乜？"), [
                ("p", "Repetitions, how long each set takes, and estimates of how far you moved. These go into your practice history and your one-page report. See <a href=\"/what-bonet-tracks\">what Bonet tracks</a> for every number it records.",
                 "次數、每組用咗幾耐，同埋你郁動幅度嘅估算。呢啲會記入你嘅練習紀錄同一頁報告。每個記錄嘅數字可以睇<a href=\"/what-bonet-tracks\">哥基健動記錄啲乜</a>。"),
            ]),
            (("Is my video private?", "我嘅影像會唔會外洩？"), [
                ("p", "Camera video and images are read on your device. They are never recorded or uploaded. Bonet keeps the count, the time and the estimates, not the video.",
                 "鏡頭影像同圖片只喺你部機讀取，唔會錄低或者上載。哥基健動只保留次數、時間同估算，唔會保留影像。"),
            ]),
            (("How accurate is the count?", "數得準唔準？"), [
                ("ul", [
                    ("The count is an estimate. Light, camera angle and loose clothing can change it.", "次數只係估算。光線、鏡頭角度同鬆身衫都會影響佢。"),
                    ("It is not a clinical measurement.", "佢唔係臨床量度。"),
                    ("Do not rely on the camera to keep you safe. It can miss a loss of balance.", "唔好靠鏡頭保障安全。佢可能留意唔到你失平衡。"),
                ]),
            ]),
            (("What do I need?", "我需要啲乜？"), [
                ("ul", [
                    ("A phone, tablet or computer with a camera and a modern web browser. Open <a href=\"https://app.bonet.care/\">app.bonet.care</a>.", "一部有鏡頭同新式瀏覽器嘅手機、平板或者電腦。打開 <a href=\"https://app.bonet.care/\">app.bonet.care</a>。"),
                    ("Enough space to move, and good light.", "夠位郁動，光線充足。"),
                    ("A stable chair, or something sturdy to hold if you stand.", "一張穩陣嘅凳；企住做嘅話，旁邊要有穩固嘅嘢扶。"),
                ]),
                ("p", "There are {exercises} exercises. Several are done seated, and you can skip, shorten or repeat any of them.", "一共有 {exercises} 個運動，有幾個係坐住做嘅；任何運動都可以跳過、縮短或者重複。"),
                ("p", "Each exercise in the <a href=\"/practice\">practice library</a> says what the camera counts for that move and how to set up.", "<a href=\"/practice\">練習庫</a>入面每個運動都講明鏡頭數啲乜同點樣擺位。"),
            ]),
            (("What does it cost?", "要幾多錢？"), ["COST"]),
            (("Is it safe for me to start?", "我開始練習安唔安全？"), [
                ("p", "Ask your doctor or therapist first. Start slow and stop if you feel pain, dizziness or unwell. Read <a href=\"/safety\">what to know before you start</a>.",
                 "請先問你嘅醫生或者治療師。慢慢開始，覺得痛、頭暈或者唔舒服就要停。請睇<a href=\"/safety\">開始之前要知嘅事</a>。"),
            ]),
        ],
    },
    # ---------------------------------------------------------------- A5
    "pricing": {
        "title": ("Bonet pricing: free plan and Premium", "哥基健動價錢：免費版同完整版"),
        "desc": ("What Bonet costs: a free plan to start, and Premium at {price} a month with 7 days free for new subscribers. What each plan includes, and how to cancel.",
                 "哥基健動要幾多錢：免費版可以即刻開始；完整版每月 {price}，新訂閱可以免費試用 7 日。每個方案包括啲乜，同埋點樣取消。"),
        "h1": ("Pricing", "價錢"),
        "answer": ("You can start Bonet free. Premium is {price} a month, with 7 days free for new subscribers, and you can cancel any time. There are no ads.",
                   "哥基健動可以免費開始。完整版每月 {price}，新訂閱可以免費試用 7 日，隨時可以取消。冇廣告。"),
        "demo": None,
        "sections": [
            (("What is in the free plan?", "免費版有啲乜？"), [
                ("ul", HOME_FREE),
            ]),
            (("What does Premium include?", "完整版有啲乜？"), [
                ("ul", HOME_PREM),
            ]),
            (("How does the free trial work?", "免費試用點樣運作？"), [
                ("p", "New subscribers get 7 days of Premium free. You can cancel any time. Renewal, cancelling and refunds are explained on the <a href=\"/subscriptions\">subscriptions page</a>.",
                 "新訂閱可以免費試用完整版 7 日，隨時可以取消。續期、取消同退款，請睇<a href=\"/subscriptions\">訂閱頁</a>。"),
            ]),
            (("Do I need to pay to try all three kinds of practice?", "要唔要俾錢先試到三種練習？"), [
                ("p", "No. The free plan includes some movement exercises, speaking practice and brain games, so you can try each kind before you decide.",
                 "唔使。免費版已經包括部分運動、說話練習同腦力遊戲，你可以逐種試過先決定。"),
            ]),
        ],
    },
}

# ---------------------------------------------------------------- A6: new section for content/therapist.html (and the 7 translated fragments)
# Two more fact pages, from the questions Jam tracks (therapists and family asking how to know home exercises were done;
# people asking for one app with movement, speech and brain games). Strings shared with /about, /camera-rep-counting and
# /for-family-and-carers are repeated word for word so they keep their translations.
_ABOUT = PAGES["about"]["sections"]
_REP_RULE = ("A repetition is counted when you reach the position, hold it for about one second, and then come back to the start. The next repetition begins after you have returned.",
             "你去到個姿勢，保持大約一秒，再返回起點，就算一下。你返回之後，先會開始下一下。")
_NOT = ("ul", [_ABOUT[2][1][0][1][0], _ABOUT[2][1][0][1][1], _ABOUT[2][1][0][1][3]])
_START = (("How do I get someone started?", "點樣幫人開始用？"), [
    ("ol", [
        ("Make sure the person agrees to use Bonet and has checked with their doctor or therapist.", "確保對方同意用哥基健動，並且已經問過佢嘅醫生或者治療師。"),
        ("Open <a href=\"https://app.bonet.care/\">app.bonet.care</a> on their phone, tablet or computer. When the app asks who will use it, say you are setting it up for someone else.", "喺佢部手機、平板或者電腦打開 <a href=\"https://app.bonet.care/\">app.bonet.care</a>。App 問邊個會用嘅時候，揀你係幫人設定。"),
        ("Answer the setup questions together. Turn on Simple mode and large text if a calmer screen helps.", "一齊答設定問題。如果簡潔啲嘅畫面有幫助，可以開簡單模式同大字。"),
        ("Clear a safe space with good light and a stable chair, and stay near for balance exercises.", "預備一個光線充足、冇雜物嘅安全空間同一張穩陣嘅凳；做平衡運動嘅時候留喺附近。"),
    ]),
])

PAGES["home-exercise-tracking"] = {
    "title": ("Tracking home exercise between therapy visits | Bonet", "喺覆診之間記錄居家練習 | 哥基健動"),
    "desc": ("How Bonet counts home exercise repetitions with the device camera and keeps a one-page report the person can share with a therapist or family. No therapist account needed. Not a medical device.",
             "哥基健動點樣用部機嘅鏡頭數居家運動次數，同埋整一頁報告，俾用戶自己同治療師或者家人分享。治療師唔使開帳戶。唔係醫療器材。"),
    "h1": ("How to know if home exercises were done", "點樣知道屋企嘅練習有冇做"),
    "answer": ("Bonet counts each repetition with the camera on the person's own device and records the days, minutes and exercises practised. The person can print or share a one-page report, for example at the next therapy visit. The counts are estimates, and Bonet is a practice tool, not a medical device.",
               "哥基健動用用戶自己部機嘅鏡頭數每一下，並記錄練習咗邊幾日、幾多分鐘同做咗咩運動。用戶可以列印或者分享一頁報告，例如喺下次覆診嘅時候。次數只係估算，哥基健動係練習工具，唔係醫療器材。"),
    "demo": ("move", 0),
    "sections": [
        (("What does Bonet record during home practice?", "喺屋企練習嘅時候，哥基健動會記錄啲乜？"), [
            ("ul", [
                ("The days practised, the minutes and the current streak.", "練習日數、分鐘同目前連續練習嘅日數。"),
                ("The exercises done, with sessions and repetitions.", "做過嘅運動，連節數同次數。"),
                ("Speaking: tries, words recognised, pace and pauses.", "說話：嘗試次數、認到嘅詞語、速度同停頓。"),
                ("Brain games played and items right.", "玩過嘅腦力遊戲同答啱嘅題數。"),
            ]),
            ("p", "Camera video is analysed on the device and never recorded or uploaded. Voice recordings are not kept.", "鏡頭影像只喺部機分析，唔會錄低或者上載。亦唔會保留錄音。"),
        ]),
        (("How does the camera count a repetition?", "鏡頭點樣數一下？"), [
            ("p",) + _REP_RULE,
            ("p", "The count is an estimate. Light, camera angle and loose clothing can make it wrong. See <a href=\"/camera-rep-counting\">how camera rep counting works</a>.",
             "次數只係估算。光線、鏡頭角度同鬆身衫都可能令佢唔準。詳情可以睇<a href=\"/camera-rep-counting\">鏡頭數次數點運作</a>。"),
        ]),
        (("How does a therapist or family member see the results?", "治療師或者家人點樣睇到結果？"), [
            ("ul", [
                ("The person prints the one-page report or shares it, for example at the next visit.", "用戶自己列印或者分享一頁報告，例如喺下次覆診嘅時候。"),
                ("The report is shared only when the person prints it or shares it. Bonet does not send it to family or therapists.", "報告只會喺用戶自己列印或者分享嘅時候先俾人睇到。哥基健動唔會將佢傳俾家人或者治療師。"),
                ("There are no dashboards, remote monitoring or alerts in the app today.", "App 而家冇儀表板、遠程監測或者警示。"),
            ]),
            ("p", "The report shows what was practised. It is not a medical record or a clinical assessment. See an <a href=\"/example-report\">example report</a>.",
             "報告顯示練習咗啲乜，唔係醫療紀錄，亦唔係臨床評估。可以睇下<a href=\"/example-report\">示範報告</a>。"),
        ]),
        (("Does a therapist need an account or pay per patient?", "治療師使唔使開帳戶，或者按病人數目俾錢？"), [
            ("p", "No. There is no therapist account and no fee per patient. Each person uses their own Bonet account, on the free plan or on Premium. A therapist only looks at the report the person chooses to share.",
             "唔使。冇治療師帳戶，亦唔會按病人數目收費。每個用戶用自己嘅哥基健動帳戶，用免費版或者完整版都得。治療師只係睇用戶自己揀分享嘅報告。"),
        ]),
        _START,
        (("What does Bonet not do?", "哥基健動唔會做啲乜？"), [_NOT]),
        (("What does it cost?", "要幾多錢？"), ["COST"]),
    ],
}

PAGES["movement-speech-brain-games"] = {
    "title": ("Movement, speaking and brain games in one home practice app | Bonet", "運動、說話同腦力遊戲，一個居家練習 app 做晒 | 哥基健動"),
    "desc": ("Bonet puts camera-counted movement exercises, speaking practice with hints and short brain games into one short daily plan for older adults at home. Not a medical device.",
             "哥基健動將鏡頭數次數嘅運動、有提示嘅說話練習同簡短腦力遊戲，放入一個簡短嘅每日計劃，俾長者喺屋企用。唔係醫療器材。"),
    "h1": ("Movement, speaking and brain games in one app", "一個 app 做運動、說話同腦力遊戲"),
    "answer": ("Bonet combines three kinds of home practice in one daily plan: {exercises} movement exercises counted by the device camera, speaking practice with hints at {levels} levels per practice type, and six short brain games. It is for older adults, including people practising after a stroke. It is a practice tool, not a medical device.",
               "哥基健動將三種居家練習放入同一個每日計劃：{exercises} 個由鏡頭數次數嘅運動、每種練習有 {levels} 級又有提示嘅說話練習，同埋六款簡短腦力遊戲。佢係為長者而設，中風後練習嘅人都用得。佢係練習工具，唔係醫療器材。"),
    "demo": ("hero", 0),
    "sections": [
        (("What is in each part?", "每個部分有啲乜？"), [("ul", _ABOUT[0][1][0][1][:3])]),
        (("How does the daily plan work?", "每日計劃點運作？"), [
            ("p", "Bonet suggests a short daily plan that mixes movement, speaking and brain games. Each step is ticked when it is done. You can skip, shorten or repeat any exercise.",
             "哥基健動會建議一個簡短嘅每日計劃，混合運動、說話同腦力遊戲。每完成一步就會打剔。任何運動都可以跳過、縮短或者重做。"),
        ]),
        (("Do I need special equipment?", "使唔使特別器材？"), [
            ("p", "No. Bonet runs in a web browser on a phone, tablet or computer with a camera and a microphone. For the movement exercises you need a stable chair and a clear space with good light.",
             "唔使。哥基健動喺有鏡頭同咪高峰嘅手機、平板或者電腦嘅瀏覽器度就用得。做運動嘅時候，你需要一張穩陣嘅凳同一個光線充足、冇雜物嘅地方。"),
        ]),
        (("Who is it for?", "啱邊個用？"), _ABOUT[1][1]),
        (("Which languages is Bonet in?", "哥基健動有邊幾種語言？"), [
            ("p", "Eight: English, Cantonese, Traditional Chinese, Simplified Chinese, Japanese, Spanish, German and French. The app, the speaking practice and this site are in all eight. Some speech recognition needs an internet connection.",
             "八種：英文、廣東話、繁體中文、簡體中文、日文、西班牙文、德文同法文。App、說話練習同呢個網站都有齊八種語言。有啲語音辨識需要連網。"),
        ]),
        (("What is Bonet not?", "哥基健動唔係乜？"), _ABOUT[2][1]),
        (("What does it cost?", "要幾多錢？"), ["COST"]),
    ],
}

# Carers searching for an Alzheimer's or dementia app. Bonet is not one in the medical sense: say so first, then only what is true.
PAGES["alzheimers-and-dementia"] = {
    "title": ("For carers of someone with Alzheimer's or dementia: a simple daily routine | Bonet", "俾照顧腦退化症家人嘅人：簡單嘅每日練習 | 哥基健動"),
    "desc": ("For carers looking for an Alzheimer's or dementia app: Bonet does not test memory or treat dementia. It is a simple daily practice routine you can do together. Not a medical device.",
             "俾搵腦退化症 app 嘅照顧者：哥基健動唔會測試記憶，亦唔會治療腦退化症。佢係一個可以一齊做嘅簡單每日練習。唔係醫療器材。"),
    "h1": ("Caring for someone with Alzheimer's or dementia? What Bonet is and is not", "照顧緊腦退化症嘅家人？哥基健動係乜、唔係乜"),
    "answer": ("Bonet is not an Alzheimer's or dementia app in the medical sense. It does not test memory, and it does not diagnose, slow, delay or treat Alzheimer's disease or any other dementia. A family member or carer can set it up as a simple daily routine to do together: gentle movement exercises, speaking practice and short brain games, with a calm Simple mode. Ask the person's doctor before starting.",
               "哥基健動唔係醫療上嘅腦退化症 app。佢唔會測試記憶，亦唔會診斷、減慢、延遲或者治療阿茲海默症或者任何腦退化症。家人或者照顧者可以將佢設定成一個一齊做嘅簡單每日練習：溫和嘅運動、說話練習同簡短腦力遊戲，仲有一個清靜嘅簡單模式。開始之前，請先問對方嘅醫生。"),
    "demo": None,
    "sections": [
        (("Can Bonet help with Alzheimer's or dementia?", "哥基健動對阿茲海默症或者腦退化症有冇幫助？"), [
            ("p", "No. Bonet does not diagnose, slow, delay, treat or prevent Alzheimer's disease or any other dementia, and it is not a memory test. No study has looked at Bonet in people with dementia. If you are worried about changes in memory, talk to a doctor.",
             "冇。哥基健動唔會診斷、減慢、延遲、治療或者預防阿茲海默症或者任何腦退化症，亦唔係記憶測試。未有任何研究喺腦退化症患者身上試過哥基健動。如果你擔心記憶有變化，請同醫生傾。"),
        ]),
        (("What could a carer use Bonet for?", "照顧者可以用哥基健動做啲乜？"), [
            ("ul", [
                ("A short daily routine of gentle movement, speaking and brain games that you do together.", "一個簡短嘅每日練習，有溫和嘅運動、說話同腦力遊戲，你哋一齊做。"),
                ("Simple mode: one big Start button instead of a busy screen.", "簡單模式：一個大大嘅開始掣，取代密密麻麻嘅畫面。"),
                ("Brain games on Easy", "腦力遊戲簡單級"),
                ("Eight languages, so practice can be in the language the person knows best.", "八種語言，可以用對方最熟悉嘅語言練習。"),
            ]),
            ("p", "Keep sessions short and stop if the person is tired, upset or confused. You know the person best.", "每次練習時間要短，如果對方攰、唔開心或者混亂，就停。你最了解對方。"),
        ]),
        _START,
        (("What should I watch for as a carer?", "作為照顧者，我要留意啲乜？"), [
            ("p", "You know the person best. Stop the session if they seem unwell, in pain or dizzy, and call your local emergency number for sudden face drooping, weakness or trouble speaking. Bonet does not watch over anyone and cannot call for help.",
             "你最了解對方。如果佢睇落唔舒服、痛或者頭暈，就停止練習；如果突然面部下垂、無力或者講嘢有困難，請打當地緊急電話。哥基健動唔會睇住任何人，亦唔可以幫手求救。"),
        ]),
        (("What is shared, and with whom?", "會分享啲乜，同邊個分享？"), [
            ("ul", [
                ("The report is shared only when the person prints it or shares it. Bonet does not send it to family or therapists.", "報告只會喺用戶自己列印或者分享嘅時候先俾人睇到。哥基健動唔會將佢傳俾家人或者治療師。"),
                ("Camera video is analysed on the device and never recorded or uploaded. Voice recordings are not kept.", "鏡頭影像只喺部機分析，唔會錄低或者上載。亦唔會保留錄音。"),
            ]),
        ]),
        (("What is Bonet not?", "哥基健動唔係乜？"), _ABOUT[2][1]),
        (("What does it cost?", "要幾多錢？"), ["COST"]),
    ],
}

THERAPIST_STEPS = (("Getting someone started", "幫人開始用"), [
    ("Open <a href=\"https://app.bonet.care/\">app.bonet.care</a> together, on the phone, tablet or computer the person will use.", "一齊喺佢會用嘅手機、平板或者電腦打開 <a href=\"https://app.bonet.care/\">app.bonet.care</a>。"),
    ("When the app asks who will use it, choose that you are setting it up for someone else.", "App 問邊個用嘅時候，揀你係幫其他人設定。"),
    ("Agree together which exercises, speaking practice and games suit the person, and for how long. The daily plan is only a suggestion; your advice comes first. Premium lets you set your own plans.", "一齊傾好邊啲運動、說話練習同遊戲啱佢，每次做幾耐。每日計劃只係建議，以你嘅意見為先。完整版可以自訂計劃。"),
    ("Show where to put the device so the camera can see them, in a clear space with a stable chair.", "示範部機要放喺邊，等鏡頭影到佢；揀個冇雜物嘅地方，加一張穩陣嘅凳。"),
    ("At the next visit, ask them to print or share their practice report. See an <a href=\"/example-report\">example report</a>.", "下次覆診時，請佢列印或者分享練習報告。可以睇下<a href=\"/example-report\">示範報告</a>。"),
])

# Accessibility statement. Only what was actually checked (axe-core scan, 14 Nov 2026) and what the site and app actually have. No conformance claim.
PAGES["accessibility"] = {
    "title": ("Accessibility statement | Bonet", "無障礙聲明 | 哥基健動"),
    "desc": ("How accessible the Bonet website and app are today: what we checked, what we fixed, what we have not tested yet, and how to tell us about a problem.",
             "哥基健動網站同 app 而家嘅無障礙情況：我哋檢查過乜、改咗乜、未測試乜，同埋點樣話俾我哋知有問題。"),
    "h1": ("Accessibility statement", "無障礙聲明"),
    "answer": ("Bonet is made for older adults, so it should be easy to see, read and use. We aim to meet the Web Content Accessibility Guidelines (WCAG) 2.2 at level AA. We do not claim that the website or the app fully meets them yet. This page says what we have checked and what we have not.",
               "哥基健動係為長者而設，所以應該易睇、易讀、易用。我哋嘅目標係達到網頁內容無障礙指引（WCAG）2.2 AA 級。我哋唔會話網站或者 app 已經完全做到。呢頁講清楚我哋檢查過乜、未檢查乜。"),
    "demo": None,
    "sections": [
        (("What have we checked?", "我哋檢查過乜？"), [
            ("p", "On 14 November 2026 we ran an automated accessibility check (axe-core) on the home page and the pricing page of this website, in several of its languages, at computer and phone screen sizes.",
             "2026 年 11 月 14 日，我哋用自動檢查工具（axe-core）檢查咗呢個網站嘅首頁同價錢頁，包括幾種語言，同埋電腦同手機嘅畫面大小。"),
            ("p", "We fixed what it found: buttons with too little colour contrast, headings out of order, buttons whose spoken name did not match their visible text, and links too small to tap easily. After the fixes, the tool reported no problems on those pages.",
             "我哋已經改好佢搵到嘅問題：有啲掣顏色對比唔夠、標題次序唔啱、有啲掣讀出嚟嘅名同畫面上嘅字唔同，同埋有啲連結細到唔易撳。改完之後，個工具喺嗰幾頁冇再報告問題。"),
            ("p", "Automated tools find only some kinds of problems. A clean result does not mean a page is fully accessible.",
             "自動工具只可以搵到部分問題。檢查結果冇問題，唔代表嗰頁完全無障礙。"),
        ]),
        (("What helps on this website?", "呢個網站有乜幫到你？"), [
            ("ul", [
                ("An A+ button at the top of every page makes the text bigger.", "每頁頂部有個 A+ 掣，可以放大文字。"),
                ("A skip link lets keyboard users jump straight to the main content.", "用鍵盤嘅人可以用「跳至內容」連結，直接去主要內容。"),
                ("If your device is set to reduce motion, most animations stop.", "如果你部機設定咗減少動態效果，大部分動畫會停。"),
                ("Animated previews have a written description for screen readers.", "動畫預覽有文字描述，俾屏幕閱讀器讀。"),
                ("Every page is in eight languages.", "每一頁都有八種語言。"),
            ]),
        ]),
        (("What helps in the app?", "App 入面有乜幫到你？"), [
            ("ul", [
                ("Simple mode: one big Start button instead of a busy screen.", "簡單模式：一個大大嘅開始掣，取代密密麻麻嘅畫面。"),
                ("A large text setting.", "大字設定。"),
                ("Eight languages, for the app and the speaking practice.", "八種語言，app 同說話練習都有。"),
            ]),
        ]),
        (("What have we not tested yet?", "我哋仲未測試乜？"), [
            ("ul", [
                ("The other pages of this website.", "呢個網站其他頁面。"),
                ("The app at app.bonet.care.", "app.bonet.care 嘅 app。"),
                ("Use with screen readers, switch access or voice control by the people who rely on them.", "由真正用開屏幕閱讀器、開關控制或者聲控嘅人親自試用。"),
            ]),
            ("p", "Some parts of practice depend on the device. Exercise counting needs the camera to see you, and some speech recognition needs an internet connection. Counts and speech results are estimates and can be wrong.",
             "有啲練習要靠部機。數運動次數要鏡頭影到你，有啲語音辨識要連網。次數同說話結果都係估算，有可能唔準。"),
        ]),
        (("How do I tell you about a problem?", "點樣話俾你哋知有問題？"), [
            ("p", "Email <a href=\"mailto:hello@coglixlabs.com\">hello@coglixlabs.com</a>. Tell us the page or screen, your device and browser, and any assistive technology you use. We will use what you tell us to decide what to fix next.",
             "請電郵 <a href=\"mailto:hello@coglixlabs.com\">hello@coglixlabs.com</a>。話俾我哋知係邊一頁或者邊個畫面、你用咩機同瀏覽器，同埋你有冇用輔助工具。我哋會根據你嘅意見決定下一步改乜。"),
        ]),
    ],
}
