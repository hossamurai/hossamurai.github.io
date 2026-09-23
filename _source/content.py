# -*- coding: utf-8 -*-
"""
Hossam TV — ALL site content lives here.
Edit this file, then run:  python build.py
Every text is written as L('English', 'العربية').
"""

def L(en, ar):
    return {'en': en, 'ar': ar}

# ----------------------------------------------------------------------------
# BASICS
# ----------------------------------------------------------------------------
SITE_NAME = 'Hossam TV'
BASE_URL = 'https://hossamurai.github.io'      # change to your custom domain later (no trailing slash)
WHATSAPP = '201117250227'                       # international format, digits only
WHATSAPP_DISPLAY = '+20 111 725 0227'
LAST_UPDATED = L('23 September 2026', '23 سبتمبر 2026')   # shown on the policies page

# Licensing text for the About page. Leave both empty to hide the section.
LICENSE_TEXT = L('', '')

# Real customer reviews (only with their permission). Leave empty to hide the section.
# Example: {'quote': L('Great football quality.', 'جودة ممتازة في المباريات.'), 'name': 'Ahmed', 'place': L('Cairo', 'القاهرة')}
REVIEWS = []

# ----------------------------------------------------------------------------
# PLANS
# stats: CHECK THESE NUMBERS — they should be your real channel / movie / series counts.
# ----------------------------------------------------------------------------
PLANS = {
    'basic': {
        'color': 'var(--c-basic)', 'img': 'basic.png', 'mono': 'B',
        'name': L('Basic', 'الأساسية'), 'aka': L('Neo 4K', 'Neo 4K'),
        'tag': L('Football and Arabic channels — the favourite of Arabic-speaking viewers.',
                 'كرة القدم والقنوات العربية — الاختيار المفضل للمشاهد العربي.'),
        'feat': [
            ('ball', L('Mainly football, plus other sports', 'كرة القدم بشكل أساسي، مع رياضات أخرى')),
            ('check', L('Strong Arabic channel line-up', 'باقة قوية من القنوات العربية')),
            ('film', L('Movies & series library', 'مكتبة أفلام ومسلسلات')),
        ],
        'stats': [('16K+', L('channels', 'قناة')), ('65K+', L('movies', 'فيلم')), ('16K+', L('series', 'مسلسل'))],
        'trial': 24, 'egypt_only': False,
        'apps': L('4K Pro · 4K Prime · 4K XCA', '4K Pro · 4K Prime · 4K XCA'),
    },
    'premium': {
        'color': 'var(--c-premium)', 'img': 'premium.png', 'mono': 'P',
        'name': L('Premium', 'بريميوم'), 'aka': L('Strong 4K', 'Strong 4K'),
        'tag': L('The biggest international library, all sports and true 4K.',
                 'أكبر مكتبة عالمية، كل الرياضات، وجودة 4K حقيقية.'),
        'feat': [
            ('check', L('About 3× the channels of Basic', 'حوالي 3 أضعاف قنوات الباقة الأساسية')),
            ('ball', L('All sports, including US sports', 'كل الرياضات، بما فيها الرياضات الأمريكية')),
            ('4k', L('4K / UHD supported', 'تدعم جودة 4K')),
        ],
        'stats': [('55K+', L('channels', 'قناة')), ('169K+', L('movies', 'فيلم')), ('44K+', L('series', 'مسلسل'))],
        'trial': 24, 'egypt_only': False,
        'apps': L('8K VIP · 8K Plus · 8K Prime', '8K VIP · 8K Plus · 8K Prime'),
    },
    'xtv': {
        'color': 'var(--c-xtv)', 'img': 'X.png', 'mono': 'X',
        'name': L('XTV', 'XTV'), 'aka': None,
        'tag': L('Our pick for Egypt: stable football and safe for the whole family.',
                 'اختيارنا لمصر: ثبات في المباريات ومناسب لكل أفراد الأسرة.'),
        'feat': [
            ('ball', L('Most stable football channels', 'أعلى ثبات لقنوات كرة القدم')),
            ('shield', L('Family-friendly — almost all mature content removed', 'مناسب للعائلة — تم حذف معظم المحتوى غير اللائق')),
            ('bolt', L('Fast updates & local support', 'تحديثات سريعة ودعم محلي')),
        ],
        'stats': [('12K+', L('channels', 'قناة')), ('19K+', L('movies', 'فيلم')), ('8K+', L('series', 'مسلسل'))],
        'trial': 12, 'egypt_only': True,
        'apps': L('XTV app', 'تطبيق XTV'),
    },
    'marvel': {
        'color': 'var(--c-marvel)', 'img': 'marvel.png', 'mono': 'M',
        'name': L('Marvel', 'Marvel'), 'aka': None,
        'tag': L("For movie and series lovers who don't mind skipping football.",
                 'لمحبي الأفلام والمسلسلات غير المهتمين بكرة القدم.'),
        'feat': [
            ('film', L('Huge movies & series library', 'مكتبة ضخمة من الأفلام والمسلسلات')),
            ('4k', L('More 4K content, clean English layout', 'محتوى 4K أكثر وواجهة إنجليزية منظمة')),
            ('x', L('Not ideal for football — choose XTV instead', 'غير مناسب لمحبي الكرة — اختر XTV'), True),
        ],
        'stats': [('6K+', L('channels', 'قناة')), ('41K+', L('movies', 'فيلم')), ('9K+', L('series', 'مسلسل'))],
        'trial': 24, 'egypt_only': True,
        'apps': L('Marvel app', 'تطبيق Marvel'),
    },
}
PLAN_ORDER = ['basic', 'premium', 'xtv', 'marvel']

CURRENCY = {
    'usd': {'en': '$', 'ar': '$', 'pre': True},
    'egp': {'en': 'EGP', 'ar': 'جنيه'},
    'sar': {'en': 'SAR', 'ar': 'ريال'},
    'aed': {'en': 'AED', 'ar': 'درهم'},
}
PERIOD = {
    'y1': L('/ year', '/ سنة'),
    'm12': L('/ 12 months', '/ 12 شهراً'),
    'm3': L('/ 3 months', '/ 3 أشهر'),
}

REGIONS = [
    {'id': 'eg', 'label': L('Egypt', 'مصر'), 'note': None, 'plans': [
        {'id': 'xtv', 'cur': 'egp', 'p1': 400, 'per': 'y1', 'p2': 700, 'featured': True, 'badge': L('Best for Egypt', 'الأفضل لمصر')},
        {'id': 'marvel', 'cur': 'egp', 'p1': 400, 'per': 'y1', 'p2': 700, 'badge': L('Movie lovers', 'لمحبي الأفلام')},
        {'id': 'basic', 'cur': 'usd', 'p1': 35, 'per': 'y1', 'p2': 60},
        {'id': 'premium', 'cur': 'usd', 'p1': 55, 'per': 'y1', 'p2': 100},
    ]},
    {'id': 'gulf', 'label': L('Saudi & Gulf', 'السعودية والخليج'),
     'note': L("Saudi Arabia, Kuwait, Qatar, Bahrain and Oman. Some apps (4K Pro, 8K VIP) aren't available in Saudi Arabia — the setup guides show which to use.",
               'السعودية والكويت وقطر والبحرين وعُمان. بعض التطبيقات (4K Pro و 8K VIP) غير متاحة في السعودية — أدلة التثبيت توضح البدائل.'),
     'plans': [
        {'id': 'basic', 'cur': 'sar', 'p1': 130, 'per': 'm12', 'featured': True, 'badge': L('Arabic & football', 'عربي وكرة قدم')},
        {'id': 'premium', 'cur': 'sar', 'p1': 200, 'per': 'm12', 'badge': L('Most content', 'أكبر محتوى')},
    ]},
    {'id': 'uae', 'label': L('UAE', 'الإمارات'),
     'note': L('UAE networks block IPTV services from time to time, so UAE subscriptions are sold for up to 3 months at a time — a smaller amount at risk for you.',
               'شبكات الإمارات تحجب خدمات IPTV من وقت لآخر، لذلك تُباع اشتراكات الإمارات لمدة 3 أشهر كحد أقصى — لتقليل المخاطرة عليك.'),
     'plans': [
        {'id': 'basic', 'cur': 'aed', 'p1': 35, 'per': 'm3', 'featured': True},
        {'id': 'premium', 'cur': 'aed', 'p1': 50, 'per': 'm3'},
    ]},
    {'id': 'intl', 'label': L('Other countries', 'دول أخرى'), 'note': None, 'plans': [
        {'id': 'basic', 'cur': 'usd', 'p1': 35, 'per': 'y1', 'p2': 60, 'featured': True, 'badge': L('Best seller', 'الأكثر مبيعاً')},
        {'id': 'premium', 'cur': 'usd', 'p1': 55, 'per': 'y1', 'p2': 100, 'badge': L('Most content', 'أكبر محتوى')},
    ]},
]

# Comparison table on the Plans page: (row label, {plan: (yes/no/None, text)})
COMPARE = [
    (L('Best for', 'الأنسب لـ'), {
        'basic': (None, L('Arabic channels & football', 'القنوات العربية وكرة القدم')),
        'premium': (None, L('Biggest library, all sports, 4K', 'أكبر مكتبة، كل الرياضات، 4K')),
        'xtv': (None, L('Stable football, families in Egypt', 'ثبات المباريات والعائلات في مصر')),
        'marvel': (None, L('Movies & series', 'الأفلام والمسلسلات')),
    }),
    (L('Football', 'كرة القدم'), {
        'basic': (True, L('Yes', 'نعم')), 'premium': (True, L('Yes', 'نعم')),
        'xtv': (True, L('Yes — most stable', 'نعم — الأعلى ثباتاً')), 'marvel': (False, L('Not the focus', 'ليست الأساس')),
    }),
    (L('Other sports', 'رياضات أخرى'), {
        'basic': (None, L('Some', 'بعضها')), 'premium': (True, L('All, incl. US sports', 'كلها، بما فيها الأمريكية')),
        'xtv': (None, L('Football first', 'التركيز على الكرة')), 'marvel': (False, L('Not the focus', 'ليست الأساس')),
    }),
    (L('Movies & series', 'أفلام ومسلسلات'), {
        'basic': (True, L('Yes', 'نعم')), 'premium': (True, L('Largest library', 'أكبر مكتبة')),
        'xtv': (True, L('Yes', 'نعم')), 'marvel': (True, L('Huge library', 'مكتبة ضخمة')),
    }),
    (L('Family-friendly', 'مناسب للعائلة'), {
        'basic': (None, L('Use app parental controls', 'عبر الرقابة الأبوية في التطبيق')),
        'premium': (None, L('Use app parental controls', 'عبر الرقابة الأبوية في التطبيق')),
        'xtv': (True, L('Mature content removed', 'تم حذف المحتوى غير اللائق')),
        'marvel': (None, L('Use app parental controls', 'عبر الرقابة الأبوية في التطبيق')),
    }),
    (L('Available in', 'متاحة في'), {
        'basic': (None, L('All countries', 'كل الدول')), 'premium': (None, L('All countries', 'كل الدول')),
        'xtv': (None, L('Egypt only', 'مصر فقط')), 'marvel': (None, L('Egypt only', 'مصر فقط')),
    }),
    (L('Free trial', 'تجربة مجانية'), {
        'basic': (True, L('24 hours', '24 ساعة')), 'premium': (True, L('24 hours', '24 ساعة')),
        'xtv': (True, L('12 hours', '12 ساعة')), 'marvel': (True, L('24 hours', '24 ساعة')),
    }),
]

# ----------------------------------------------------------------------------
# APPS & SETUP
# ----------------------------------------------------------------------------
APPS = {
    'basic': [
        {'name': '4K Pro', 'code': 'tinyurl.com/my4kpro', 'rec': True, 'warn': ['uaeksa']},
        {'name': '4K Prime', 'code': 'tinyurl.com/my4kprime'},
        {'name': '4K XCA', 'code': 'tinyurl.com/my4kxca'},
    ],
    'premium': [
        {'name': '8K VIP', 'code': 'tinyurl.com/my8kvip', 'rec': True, 'warn': ['firestick', 'uaeksa']},
        {'name': '8K Plus', 'code': 'tinyurl.com/my8kplus'},
        {'name': '8K Prime', 'code': 'tinyurl.com/my8kprime'},
    ],
    'xtv': [{'name': 'XTV', 'code': 'tinyurl.com/xapppro'}],
    'marvel': [{'name': 'Marvel', 'code': 'tinyurl.com/appmrvl'}],
}
WARN = {
    'uaeksa': L('Not available in UAE & Saudi Arabia', 'غير متاح في الإمارات والسعودية'),
    'firestick': L("Doesn't work on Firestick", 'لا يعمل على فايرستيك'),
}
SMARTERS = 'tinyurl.com/smrtsapp'
SMARTERS_VIDEO = 'https://youtu.be/jLxBqAIdYns'
SFVIP_ZIP = 'https://www.mediafire.com/file/sghsre0rgcuiemb/SFVIP_Player_x64.zip/file'
SFVIP_VIDEO = 'https://youtu.be/dESni3uxAa4'

# ----------------------------------------------------------------------------
# PAYMENT METHODS (information only)
# ----------------------------------------------------------------------------
PAY_EGYPT = [
    ('InstaPay', L('Instant', 'فوري')),
    ('Vodafone Cash', L('Instant', 'فوري')),
]
PAY_ABROAD = [
    ('TapTap Send', L('No transfer fees · debit card', 'بدون رسوم تحويل · بطاقة خصم')),
    ('PayPal', L('Friends & Family · you cover the fee', 'Friends & Family · الرسوم على العميل')),
    ('Sendwave', L('Debit card', 'بطاقة خصم')),
    ('Whish Money', L('You cover the fee', 'الرسوم على العميل')),
    (L('Bank transfer', 'تحويل بنكي'), L('Saudi Arabia · Egypt · Europe', 'السعودية · مصر · أوروبا')),
]

# ----------------------------------------------------------------------------
# CHANNELS PAGE — categories. "best" = plans that are strongest in that category.
# CHECK: adjust to match your real line-ups.
# ----------------------------------------------------------------------------
CATEGORIES = [
    ('ball', L('Live sports', 'الرياضة المباشرة'),
     L('Live football every week, plus other sports. Premium adds the widest range, including US sports.',
       'مباريات كرة القدم مباشرة كل أسبوع، بالإضافة إلى رياضات أخرى. باقة بريميوم تضيف أوسع تشكيلة، بما فيها الرياضات الأمريكية.'),
     ['xtv', 'basic', 'premium']),
    ('globe', L('Arabic channels', 'القنوات العربية'),
     L('Egyptian, Gulf and pan-Arab channels for entertainment, drama and religion.',
       'قنوات مصرية وخليجية وعربية للترفيه والدراما والبرامج الدينية.'),
     ['basic', 'xtv']),
    ('tv', L('International', 'القنوات العالمية'),
     L('Channels from Europe, the US and beyond — useful if you live abroad.',
       'قنوات من أوروبا وأمريكا ودول أخرى — مفيدة إذا كنت تعيش خارج بلدك.'),
     ['premium']),
    ('film', L('Movies', 'الأفلام'),
     L('Arabic and international films on demand, with new releases added regularly.',
       'أفلام عربية وعالمية عند الطلب، وتُضاف الإصدارات الجديدة باستمرار.'),
     ['premium', 'marvel']),
    ('series', L('Series', 'المسلسلات'),
     L('Full seasons of Arabic, Turkish and international series, ready to binge.',
       'مواسم كاملة من المسلسلات العربية والتركية والعالمية.'),
     ['premium', 'marvel']),
    ('kids', L('Kids & family', 'الأطفال والعائلة'),
     L('Cartoons and family channels. XTV has almost all mature content removed.',
       'قنوات كرتون وعائلية. سيرفر XTV تم حذف معظم المحتوى غير اللائق منه.'),
     ['xtv']),
    ('info', L('News', 'الأخبار'),
     L('Arabic and international news channels, live around the clock.',
       'قنوات إخبارية عربية وعالمية على مدار الساعة.'),
     ['basic', 'premium']),
    ('4k', L('4K & UHD', 'محتوى 4K'),
     L('Selected channels and films in 4K — you need a 4K device and about 25 Mbps.',
       'قنوات وأفلام مختارة بجودة 4K — تحتاج جهازاً يدعم 4K وسرعة حوالي 25 ميجابت.'),
     ['premium', 'marvel']),
]

# ----------------------------------------------------------------------------
# FAQ  (group -> list of (id, question, answer-html))
# ----------------------------------------------------------------------------
FAQ = [
    (L('General', 'أسئلة عامة'), [
        ('what-is-iptv', L('What is IPTV?', 'ما هو الـ IPTV؟'),
         L('IPTV lets you watch live TV channels, sports and movies over the internet instead of satellite or cable.',
           'خدمة تتيح لك مشاهدة القنوات والمباريات والأفلام عبر الإنترنت بدلاً من الدش أو الكابل.')),
        ('what-do-i-need', L('What do I need?', 'ماذا أحتاج لتشغيل الخدمة؟'),
         L('A stable internet connection and a supported device: Android TV or box, Firestick (not Vega OS models), Samsung/LG Smart TV, Android phone, iPhone, iPad, Mac, Apple TV or a Windows PC.',
           'اتصال إنترنت مستقر وجهاز مدعوم: أندرويد تي في أو بوكس، فايرستيك (عدا أجهزة Vega OS)، شاشة سامسونج أو LG، موبايل أندرويد، آيفون، آيباد، ماك، أبل تي في، أو كمبيوتر ويندوز.')),
        ('free-trial', L('Is there a free trial?', 'هل توجد تجربة مجانية؟'),
         L('Yes — 12 hours for XTV and 24 hours for every other plan. One trial per customer. Request it on WhatsApp.',
           'نعم — 12 ساعة لسيرفر XTV و24 ساعة لباقي الباقات. تجربة واحدة لكل عميل. اطلبها عبر واتساب.')),
        ('family', L('Is it safe for families?', 'هل الخدمة مناسبة للعائلة؟'),
         L("We don't offer adult channels, but some movies and series can contain mature scenes. XTV is our family-friendly option, with almost all mature content removed, and many apps have parental controls.",
           'لا نوفر قنوات للكبار، لكن بعض الأفلام والمسلسلات قد تحتوي على مشاهد غير مناسبة. سيرفر XTV هو الخيار العائلي وتم حذف معظم المحتوى غير اللائق منه، كما تحتوي كثير من التطبيقات على رقابة أبوية.')),
        ('channels', L('Which channels are included?', 'ما القنوات المتاحة؟'),
         L('Sports (mainly football), Arabic and international channels, movies, series, news and kids. Exact line-ups vary by plan — see the {channels} page, or ask us on WhatsApp for the latest list.',
           'قنوات رياضية (كرة القدم بشكل أساسي)، قنوات عربية وعالمية، أفلام، مسلسلات، أخبار، وأطفال. القائمة تختلف حسب الباقة — راجع صفحة {channels}، أو اطلب أحدث قائمة عبر واتساب.')),
    ]),
    (L('Plans, payment & renewal', 'الباقات والدفع والتجديد'), [
        ('which-plan', L('Which plan should I choose?', 'أي باقة أختار؟'),
         L('In Egypt: <b>XTV</b> for football and families, <b>Marvel</b> for movies and series. Everywhere else: <b>Basic</b> for Arabic channels and football, <b>Premium</b> for the biggest library, all sports and 4K. Not sure? Try one free first.',
           'في مصر: <b>XTV</b> للكرة والعائلة، و<b>Marvel</b> للأفلام والمسلسلات. في باقي الدول: <b>الأساسية</b> للقنوات العربية والكرة، و<b>بريميوم</b> لأكبر مكتبة وكل الرياضات وجودة 4K. غير متأكد؟ جرّب مجاناً أولاً.')),
        ('how-to-pay', L('How do I pay?', 'كيف أدفع؟'),
         L('In Egypt: InstaPay or Vodafone Cash. From abroad: TapTap Send, PayPal, Sendwave, Whish Money or bank transfer. Message us on WhatsApp and we\'ll send the details, then send a clear screenshot of your receipt.',
           'داخل مصر: إنستاباي أو فودافون كاش. من خارج مصر: TapTap Send أو PayPal أو Sendwave أو Whish Money أو تحويل بنكي. راسلنا عبر واتساب لنرسل لك البيانات، ثم أرسل صورة واضحة للإيصال.')),
        ('activation', L('How long does activation take?', 'كم يستغرق التفعيل؟'),
         L('After you send a clear screenshot of your payment on WhatsApp, activation usually takes a few minutes. Please allow up to 24 hours.',
           'بعد إرسال صورة واضحة لإيصال الدفع عبر واتساب، يتم التفعيل عادةً خلال دقائق، وبحد أقصى 24 ساعة.')),
        ('renew', L('Does my subscription renew automatically?', 'هل يتجدد الاشتراك تلقائياً؟'),
         L("No. Message us on WhatsApp when it's time to renew. Subscriptions can't be paused.",
           'لا. راسلنا عبر واتساب عند موعد التجديد. لا يمكن إيقاف الاشتراك مؤقتاً.')),
        ('change-plan', L('Can I change or upgrade my plan?', 'هل يمكنني تغيير الباقة أو ترقيتها؟'),
         L('Yes — once your current subscription ends, you can renew on any plan available in your country.',
           'نعم — بعد انتهاء اشتراكك الحالي يمكنك التجديد على أي باقة متاحة في بلدك.')),
        ('refund', L('Can I get a refund?', 'هل يمكن استرجاع المبلغ؟'),
         L("There are no refunds after activation — that's why we offer a free trial first.",
           'لا يوجد استرجاع للمبلغ بعد التفعيل — ولهذا نوفر تجربة مجانية أولاً.')),
        ('uae', L('Why are UAE plans only 3 months?', 'لماذا اشتراكات الإمارات 3 أشهر فقط؟'),
         L('UAE networks block IPTV services from time to time. Shorter subscriptions mean less of your money is at risk if that happens.',
           'شبكات الإمارات تحجب خدمات IPTV من وقت لآخر. الاشتراك الأقصر يعني مخاطرة أقل على أموالك إذا حدث ذلك.')),
    ]),
    (L('Devices & watching', 'الأجهزة والمشاهدة'), [
        ('multi-device', L('Can I use it on more than one device?', 'هل يمكنني التشغيل على أكثر من جهاز؟'),
         L('You can install it on as many devices as you like and share it with family, but only one device can watch at a time. Watching on two at once can lock the account.',
           'يمكنك التثبيت على أي عدد من الأجهزة ومشاركته مع العائلة، لكن المشاهدة تكون على جهاز واحد فقط في نفس الوقت. التشغيل على جهازين معاً قد يوقف الحساب.')),
        ('speed', L('What internet speed do I need?', 'ما سرعة الإنترنت المطلوبة؟'),
         L('About 5 Mbps for SD, 10 Mbps for Full HD and 25 Mbps or more for 4K (plus a 4K-capable device).',
           'حوالي 5 ميجابت لجودة SD، و10 ميجابت لجودة Full HD، و25 ميجابت أو أكثر لجودة 4K (مع جهاز يدعم 4K).')),
        ('firestick', L('Does it work on my Firestick?', 'هل يعمل على الفايرستيك؟'),
         L('Most Firesticks work. The exception is newer models running Vega OS (like the Fire TV Stick 4K Select and the 2026 Fire TV Stick HD), which can\'t install IPTV apps. Check under <b>Settings → My Fire TV → About</b>: "Fire OS" is fine; plain "OS" with a version starting with 1 means Vega OS.',
           'معظم أجهزة الفايرستيك تعمل. الاستثناء هو الأجهزة الأحدث بنظام Vega OS (مثل Fire TV Stick 4K Select و Fire TV Stick HD إصدار 2026) لأنها لا تسمح بتثبيت تطبيقات IPTV. للتأكد: <b><bdi dir="ltr">Settings → My Fire TV → About</bdi></b>. إذا كان مكتوباً Fire OS فجهازك مناسب، أما إذا كان مكتوباً OS فقط ويبدأ الرقم بـ 1 فهو Vega OS.')),
        ('smart-tv-fee', L('Is there an extra fee for Samsung or LG TVs?', 'هل توجد رسوم إضافية لشاشات سامسونج و LG؟'),
         L('Smart TVs use IBO Player or Bob Player. With Basic and Premium, activation is free for your first TV and $4 (lifetime) for each extra TV. With XTV and Marvel, the app costs 100 EGP a year or 200 EGP lifetime per TV, after a 7-day free trial.',
           'الشاشات الذكية تستخدم تطبيق IBO Player أو Bob Player. مع الباقة الأساسية وبريميوم، التفعيل مجاني لأول شاشة و4 دولارات (مدى الحياة) لكل شاشة إضافية. مع XTV و Marvel، يكلف التطبيق 100 جنيه سنوياً أو 200 جنيه مدى الحياة لكل شاشة، بعد تجربة مجانية 7 أيام.')),
        ('roku', L('Do you support Roku?', 'هل تدعمون روكو؟'),
         L('No. An Android TV box or a Firestick running Fire OS (not Vega OS) is the easiest alternative.',
           'لا. أسهل بديل هو أندرويد بوكس أو فايرستيك بنظام Fire OS (وليس Vega OS).')),
    ]),
]

# ----------------------------------------------------------------------------
# TROUBLESHOOTING (help page) — (id, title, answer-html)
# ----------------------------------------------------------------------------
TROUBLE = [
    ('buffering', L('Buffering or freezing', 'التقطيع أو التجميد'),
     L('<ol><li>Unplug your router and TV/device for 10 seconds, plug them back in and wait for the internet to come back.</li>'
       '<li>Test your speed at <a href="https://fast.com" target="_blank" rel="noopener">fast.com</a> — you need about 10 Mbps for Full HD and 25 Mbps for 4K.</li>'
       '<li>Use a network cable or 5 GHz Wi-Fi if you can, and pause big downloads on other devices.</li>'
       '<li>Try one of the other apps for your plan from the setup guide.</li>'
       '<li>On Android devices, clear the app cache: <b>Settings → Apps → (the app) → Storage → Clear cache</b>.</li></ol>',
       '<ol><li>افصل الراوتر والتلفزيون/الجهاز من الكهرباء لمدة 10 ثوانٍ، ثم أعد توصيلهما وانتظر عودة الإنترنت.</li>'
       '<li>اختبر سرعتك على <a href="https://fast.com" target="_blank" rel="noopener">fast.com</a> — تحتاج حوالي 10 ميجابت لجودة Full HD و25 ميجابت لجودة 4K.</li>'
       '<li>استخدم كابل إنترنت أو شبكة واي فاي 5 GHz إن أمكن، وأوقف التحميلات الكبيرة على الأجهزة الأخرى.</li>'
       '<li>جرّب أحد التطبيقات الأخرى الخاصة بباقتك من دليل التثبيت.</li>'
       '<li>على أجهزة أندرويد، امسح ذاكرة التطبيق المؤقتة: <b>الإعدادات ← التطبيقات ← (التطبيق) ← التخزين ← مسح ذاكرة التخزين المؤقت</b>.</li></ol>')),
    ('login', L("I can't sign in", 'لا أستطيع تسجيل الدخول'),
     L('<ol><li>Type the username and password exactly as we sent them — they are case-sensitive and have no spaces.</li>'
       '<li>Make sure you are using an app for <b>your</b> plan (for example, 4K apps are for Basic, 8K apps are for Premium).</li>'
       '<li>Check that your subscription hasn\'t expired.</li>'
       '<li>Still not working? Send us a screenshot of the error on WhatsApp.</li></ol>',
       '<ol><li>اكتب اسم المستخدم وكلمة المرور كما أرسلناهما تماماً — الحروف الكبيرة والصغيرة مهمة ولا توجد مسافات.</li>'
       '<li>تأكد أنك تستخدم تطبيق باقتك <b>أنت</b> (مثلاً تطبيقات 4K للباقة الأساسية، وتطبيقات 8K لباقة بريميوم).</li>'
       '<li>تأكد أن اشتراكك لم ينتهِ.</li>'
       '<li>ما زالت المشكلة قائمة؟ أرسل لنا صورة لرسالة الخطأ عبر واتساب.</li></ol>')),
    ('locked', L('It stopped working suddenly', 'الخدمة توقفت فجأة'),
     L('<ol><li>Make sure no one else is watching on your account — two screens at the same time can lock it.</li>'
       '<li>Restart your router and device (unplug for 10 seconds).</li>'
       '<li>Check our WhatsApp Status for maintenance news.</li>'
       '<li>Then message us and we\'ll check your account.</li></ol>',
       '<ol><li>تأكد أنه لا يوجد شخص آخر يشاهد على حسابك — التشغيل على شاشتين في نفس الوقت قد يوقفه.</li>'
       '<li>أعد تشغيل الراوتر والجهاز (افصلهما من الكهرباء لمدة 10 ثوانٍ).</li>'
       '<li>تابع حالة الواتساب الخاصة بنا لأخبار الصيانة.</li>'
       '<li>ثم راسلنا وسنفحص حسابك.</li></ol>')),
    ('install', L("The app won't install", 'التطبيق لا يتم تثبيته'),
     L('<ul><li><b>Firestick:</b> turn on <b>Settings → My Fire TV → Developer options → Install unknown apps → Downloader</b>. No Developer options? Open <b>About</b> and click your device name 7 times.</li>'
       '<li><b>Android TV / box:</b> allow Downloader to install unknown apps when asked, or look under <b>Settings → Apps → Security &amp; restrictions → Unknown sources</b> (the path differs by brand).</li>'
       '<li><b>Phone:</b> when your phone asks, allow your browser to install apps. If Play Protect warns you, tap <b>More details → Install anyway</b>.</li>'
       '<li>Make sure you tapped the <b>big blue Download</b> button on MediaFire — not "Download faster".</li></ul>',
       '<ul><li><b>فايرستيك:</b> فعّل <b><bdi dir="ltr">Settings → My Fire TV → Developer options → Install unknown apps → Downloader</bdi></b>. لا تجد Developer options؟ افتح <b>About</b> واضغط على اسم جهازك 7 مرات.</li>'
       '<li><b>أندرويد تي في / بوكس:</b> اسمح لتطبيق Downloader بتثبيت التطبيقات عند السؤال، أو من <b>الإعدادات ← التطبيقات ← الأمان والقيود ← مصادر غير معروفة</b> (المسار يختلف حسب الشركة).</li>'
       '<li><b>الموبايل:</b> عندما يسألك الهاتف، اسمح للمتصفح بتثبيت التطبيقات. إذا ظهر تحذير Play Protect، اضغط <b>مزيد من التفاصيل ← التثبيت على أي حال</b>.</li>'
       '<li>تأكد أنك ضغطت زر التحميل <b>الأزرق الكبير</b> في MediaFire — وليس «Download faster».</li></ul>')),
    ('channel', L('One channel or movie isn\'t working', 'قناة أو فيلم واحد لا يعمل'),
     L('Individual channels sometimes go down for a short time. Try again in a few minutes or switch to another app for your plan. If it\'s still down, send us the channel name on WhatsApp.',
       'أحياناً تتوقف قناة معينة لفترة قصيرة. جرّب مرة أخرى بعد دقائق أو استخدم تطبيقاً آخر لباقتك. إذا استمرت المشكلة، أرسل لنا اسم القناة عبر واتساب.')),
]

# ----------------------------------------------------------------------------
# DEVICES
# ----------------------------------------------------------------------------
DEVICES = [
    {'slug': 'android-tv', 'icon': 'androidtv', 'name': L('Android TV & TV boxes', 'أندرويد تي في والبوكس'),
     'short': L('Downloader app · 10 min', 'تطبيق Downloader · 10 دقائق')},
    {'slug': 'firestick', 'icon': 'stick', 'name': L('Amazon Firestick', 'أمازون فايرستيك'),
     'short': L('Downloader app · 10 min', 'تطبيق Downloader · 10 دقائق')},
    {'slug': 'android', 'icon': 'phone', 'name': L('Android phone & tablet', 'موبايل وتابلت أندرويد'),
     'short': L('Direct download · 5 min', 'تحميل مباشر · 5 دقائق')},
    {'slug': 'apple', 'icon': 'apple', 'name': L('iPhone, iPad, Mac & Apple TV', 'آيفون وآيباد وماك وأبل تي في'),
     'short': L('App Store · 5 min', 'App Store · 5 دقائق')},
    {'slug': 'smart-tv', 'icon': 'tv', 'name': L('Samsung & LG Smart TV', 'شاشات سامسونج و LG'),
     'short': L('IBO / Bob Player', 'IBO / Bob Player')},
    {'slug': 'windows', 'icon': 'laptop', 'name': L('Windows PC & laptop', 'كمبيوتر ولابتوب ويندوز'),
     'short': L('SFVIP Player · 5 min', 'SFVIP Player · 5 دقائق')},
    {'slug': 'roku', 'icon': 'box', 'name': L('Roku', 'روكو'),
     'short': L('Not supported', 'غير مدعوم'), 'off': True},
]
