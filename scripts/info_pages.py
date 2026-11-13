"""Fact pages built by seo_pages.py in every language, with the same schema as seo_pages.PAGES:
  /about                plain facts about Bonet (also the place that says Bonet is not the app Bold)
  /camera-rep-counting  how the camera counts repetitions, kept consistent with the practice library wording
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
THERAPIST_STEPS = (("Getting someone started", "幫人開始用"), [
    ("Open <a href=\"https://app.bonet.care/\">app.bonet.care</a> together, on the phone, tablet or computer the person will use.", "一齊喺佢會用嘅手機、平板或者電腦打開 <a href=\"https://app.bonet.care/\">app.bonet.care</a>。"),
    ("When the app asks who will use it, choose that you are setting it up for someone else.", "App 問邊個用嘅時候，揀你係幫其他人設定。"),
    ("Agree together which exercises, speaking practice and games suit the person, and for how long. The daily plan is only a suggestion; your advice comes first. Premium lets you set your own plans.", "一齊傾好邊啲運動、說話練習同遊戲啱佢，每次做幾耐。每日計劃只係建議，以你嘅意見為先。完整版可以自訂計劃。"),
    ("Show where to put the device so the camera can see them, in a clear space with a stable chair.", "示範部機要放喺邊，等鏡頭影到佢；揀個冇雜物嘅地方，加一張穩陣嘅凳。"),
    ("At the next visit, ask them to print or share their practice report. See an <a href=\"/example-report\">example report</a>.", "下次覆診時，請佢列印或者分享練習報告。可以睇下<a href=\"/example-report\">示範報告</a>。"),
])
