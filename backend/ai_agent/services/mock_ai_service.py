"""
Mock AI Service - Now powered by RAG (Retrieval-Augmented Generation).
Retrieves real data from the database to answer user queries.
Generates natural, conversational responses like ChatGPT.
Falls back to hardcoded responses only when no database content is found.
"""
import logging
import random

from .rag_service import RAGService

logger = logging.getLogger(__name__)


class MockAIService:
    def __init__(self):
        self.supported_languages = ['en', 'fa', 'ps']
        self.rag = RAGService()
        logger.info("MockAIService initialized with RAG - Retrieving real data from database")

    def generate_response(self, message, language='en'):
        logger.info(f"Mock AI generating response for: '{message}' in {language}")

        # Detect intent
        intent = self.rag.detect_intent(message)
        logger.info(f"Detected intent: {intent}")

        # Retrieve context from database using RAG
        context = self.rag.retrieve_context(message, language, top_k=3)

        if context:
            # We have real data from the database - format it conversationally
            response = self._format_natural_response(context, intent, language)
            logger.info(f"RAG response generated for intent: {intent}")
            return response

        # No database content found - fall back to hardcoded responses
        logger.info(f"No RAG context found, using fallback responses for intent: {intent}")
        return self._get_fallback_response(intent, language)

    def _format_natural_response(self, context: str, intent: str, language: str) -> str:
        """Format the RAG context into a natural, conversational response like ChatGPT."""
        
        # Natural conversational templates per intent and language
        templates = {
            'en': {
                'greeting': "Hello! Welcome to Afghan Connect AI Support. {context} How can I assist you today?",
                'balance': "Let me check that for you! {context} Is there anything else you'd like to know about your account?",
                'package': "Great question! Here are the internet packages we currently have available: {context} Would you like to subscribe to any of these? Just dial the activation code and you're all set!",
                'coverage': "Let me look up the coverage information for you: {context} If you need details about a specific area, just let me know!",
                'sim': "I'd be happy to help with SIM registration! {context} Feel free to visit any of our service centers for assistance.",
                'technical': "I understand you're having some technical difficulties. Let me share some helpful information: {context} If the issue continues, please don't hesitate to reach out to our support team at 0799000000.",
                'default': "Thanks for reaching out! Here's what I found: {context} Let me know if you need any more help!"
            },
            'fa': {
                'greeting': "سلام! به پشتیبانی هوش مصنوعی افغان اتصال خوش آمدید. {context} امروز چگونه می توانم به شما کمک کنم؟",
                'balance': "بگذارید این را برای شما بررسی کنم! {context} آیا چیز دیگری در مورد حساب خود می خواهید بدانید؟",
                'package': "سوال عالی! در اینجا بسته های اینترنتی که در حال حاضر موجود هستند: {context} آیا می خواهید در یکی از اینها مشترک شوید؟ کافیست کد فعال سازی را شماره گیری کنید!",
                'coverage': "بگذارید اطلاعات پوشش را برای شما پیدا کنم: {context} اگر به جزئیات یک منطقه خاص نیاز دارید، فقط به من بگویید!",
                'sim': "خوشحالم که می توانم با ثبت سیم کمک کنم! {context} برای کمک، می توانید به هر یک از مراکز خدمات ما مراجعه کنید.",
                'technical': "متوجه شدم که با مشکلات فنی روبرو هستید. بگذارید اطلاعات مفیدی را با شما به اشتراک بگذارم: {context} اگر مشکل ادامه داشت، لطفاً با تیم پشتیبانی ما در 0799000000 تماس بگیرید.",
                'default': "از تماس شما متشکرم! در اینجا آنچه پیدا کردم: {context} اگر به کمک بیشتری نیاز دارید، به من بگویید!"
            },
            'ps': {
                'greeting': "سلام! د افغان اتصال د AI ملاتړ ته ښه راغلئ. {context} زه نن څنګه تاسو سره مرسته کولی شم؟",
                'balance': "راځئ چې دا ستاسو لپاره وګورم! {context} ایا تاسو د خپل حساب په اړه نور څه پوهیدل غواړئ؟",
                'package': "ښه پوښتنه! دلته هغه انټرنیټ پیکیجونه دي چې اوس مهال شتون لري: {context} ایا تاسو غواړئ په دې کې ګډون وکړئ؟ یوازې د فعالولو کوډ ډایل کړئ!",
                'coverage': "راځئ چې ستاسو لپاره د پوښښ معلومات پیدا کړم: {context} که تاسو د یوې خاصې سیمې په اړه تفصیل ته اړتیا لرئ، یوازې ماته ووایاست!",
                'sim': "زه خوشحال یم چې د سیم ثبتولو کې مرسته کولی شم! {context} د مرستې لپاره، تاسو کولی شئ زموږ د خدمت هر مرکز ته مراجعه وکړئ.",
                'technical': "زه پوهیږم چې تاسو د تخنیکي ستونزو سره مخ یاست. راځئ چې ځینې ګټور معلومات له تاسو سره شریک کړم: {context} که ستونزه دوام وکړي، مهرباني وکړئ زموږ د ملاتړ ټیم سره په 0799000000 کې اړیکه ونیسئ.",
                'default': "د اړیکې لپاره مننه! دلته هغه څه دي چې ما وموندل: {context} که تاسو نورې مرستې ته اړتیا لرئ، ماته ووایاست!"
            }
        }

        lang_templates = templates.get(language, templates['en'])
        template = lang_templates.get(intent, lang_templates['default'])
        
        return template.format(context=context)

    def _get_fallback_response(self, intent: str, language: str) -> str:
        """Fallback hardcoded responses when no database content is found."""
        responses = {
            'en': {
                'greeting': [
                    "Hello! Welcome to Afghan Connect AI Support. I'm here to help you with balance checks, internet packages, network coverage, SIM registration, and technical support. How can I assist you today?",
                    "Hi there! Thank you for contacting Afghan Connect customer support. What can I help you with today?",
                    "Welcome to Afghan Connect! I'm your AI assistant. How can I help you with our services today?"
                ],
                'balance': [
                    "You can check your balance by dialing *123# from your Afghan Connect number. Your current balance and validity will be displayed immediately.",
                    "To check your balance, simply dial *123#. You'll see your main balance, data balance, and any active packages.",
                    "For balance inquiry, dial *123# from your Afghan Connect SIM. You can also check your balance through the MyConnect mobile app."
                ],
                'package': [
                    "We offer several internet packages:\n- Basic: 100 AFN - 1GB for 7 days\n- Standard: 200 AFN - 3GB for 15 days\n- Premium: 500 AFN - 10GB for 30 days\n- Super: 800 AFN - 20GB for 30 days\n\nTo subscribe, dial *123*1# and follow the instructions.",
                    "Available internet packages:\n- Basic (1GB/7 days): 100 AFN\n- Standard (3GB/15 days): 200 AFN\n- Premium (10GB/30 days): 500 AFN\n- Super (20GB/30 days): 800 AFN\n\nDial *123*1# to subscribe to any package."
                ],
                'coverage': [
                    "Afghan Connect has extensive coverage across all 34 provinces with strong 4G signals in urban areas and reliable coverage in rural regions. Our network covers over 90% of populated areas.",
                    "We provide nationwide coverage with excellent signal quality in Kabul, Herat, Mazar-i-Sharif, Kandahar, Jalalabad, Kunduz, and other major cities. Coverage is continuously expanding.",
                    "Our network covers all major cities and most rural areas. You can check specific coverage in your area by visiting our website or dialing *123# for network information."
                ],
                'sim': [
                    "For SIM registration, please visit any Afghan Connect service center with your original Tazkira ID card. The process takes about 15-20 minutes and is completely free.",
                    "To register your SIM card, bring your original Tazkira to the nearest Afghan Connect office. Registration is mandatory and helps ensure network security.",
                    "SIM registration requires your original Tazkira ID. Visit any of our service centers - we have locations in all major cities. The process is quick and free of charge."
                ],
                'technical': [
                    "For network issues, try these steps: 1) Restart your device 2) Check if you're in a coverage area 3) Ensure data is enabled 4) Try manual network selection. If issues persist, visit our service center.",
                    "Common troubleshooting: Restart your phone, check SIM card placement, ensure mobile data is enabled, and verify you have network coverage. For persistent issues, contact technical support at 0799000000.",
                    "If you're experiencing network problems: 1) Restart your device 2) Check coverage in your area 3) Verify your SIM is properly inserted 4) Ensure you have active balance. Need more help? Call 0799000000."
                ],
                'default': [
                    "Thank you for your inquiry. I'm here to help with Afghan Connect services including balance checks, internet packages, network coverage, SIM registration, and technical support. For more specific assistance, you can also contact our customer service at 0799000000.",
                    "I understand you're looking for assistance. I can help with various Afghan Connect services. Could you please provide more details about what you need help with?",
                    "I'm here to assist you with Afghan Connect services. Whether it's about your balance, internet packages, network coverage, or technical issues, I'm ready to help. You can also reach our support team at 0799000000."
                ]
            },
            'fa': {
                'greeting': [
                    "سلام! به پشتیبانی هوش مصنوعی افغان اتصال خوش آمدید. من می توانم در مورد بررسی بیلانس، بسته های اینترنتی، پوشش شبکه، ثبت سیم و پشتیبانی فنی به شما کمک کنم. چگونه می توانم امروز به شما کمک کنم؟",
                    "درود! از تماس شما با پشتیبانی مشتریان افغان اتصال سپاسگزاریم. امروز چه کمکی می توانم به شما بکنم؟",
                    "سلام! به افغان اتصال خوش آمدید. من دستیار هوش مصنوعی شما هستم. چگونه می توانم در مورد خدمات ما به شما کمک کنم؟"
                ],
                'balance': [
                    "شما می‌توانید با شماره‌گیری *123# از شماره افغان اتصال خود، بیلانس خود را بررسی کنید. بیلانس فعلی و اعتبار شما بلافاصله نمایش داده می‌شود.",
                    "برای بررسی بیلانس، کافیست *123# را شماره گیری کنید. بیلانس اصلی، بیلانس دیتا و هر بسته فعالی را مشاهده خواهید کرد.",
                    "برای استعلام بیلانس، *123# را از سیم کارت افغان اتصال خود شماره گیری کنید. همچنین می‌توانید از اپلیکیشن MyConnect استفاده کنید."
                ],
                'package': [
                    "ما چندین بسته اینترنتی ارائه می‌دهیم:\n- پایه: 100 افغانی - 1 گیگابایت برای 7 روز\n- استاندارد: 200 افغانی - 3 گیگابایت برای 15 روز\n- پریمیوم: 500 افغانی - 10 گیگابایت برای 30 روز\n- سوپر: 800 افغانی - 20 گیگابایت برای 30 روز\n\nبرای اشتراک، *123*1# را شماره گیری کرده و دستورات را دنبال کنید.",
                    "بسته های اینترنتی موجود:\n- پایه (1 گیگابایت/7 روز): 100 افغانی\n- استاندارد (3 گیگابایت/15 روز): 200 افغانی\n- پریمیوم (10 گیگابایت/30 روز): 500 افغانی\n- سوپر (20 گیگابایت/30 روز): 800 افغانی\n\nبرای اشتراک هر بسته، *123*1# را شماره گیری کنید."
                ],
                'coverage': [
                    "افغان اتصال پوشش گسترده در تمام 34 ولایت با سیگنال 4G قوی در مناطق شهری و پوشش مطمئن در مناطق روستایی دارد. شبکه ما بیش از 90٪ مناطق مسکونی را پوشش می دهد.",
                    "ما پوشش سراسری با کیفیت سیگنال عالی در کابل، هرات، مزارشریف، قندهار، جلال آباد، کندز و سایر شهرهای بزرگ ارائه می دهیم. پوشش به طور مداوم در حال گسترش است.",
                    "شبکه ما تمام شهرهای بزرگ و اکثر مناطق روستایی را پوشش می دهد. برای بررسی پوشش خاص در منطقه خود، به وب سایت ما مراجعه کنید یا برای اطلاعات شبکه *123# را شماره گیری کنید."
                ],
                'sim': [
                    "برای ثبت سیم کارت، لطفاً به هر مرکز خدمات افغان اتصال با کارت شناسایی تذکره اصلی مراجعه کنید. این فرآیند حدود 15-20 دقیقه طول می‌کشد و کاملاً رایگان است.",
                    "برای ثبت سیم کارت خود، تذکره اصلی خود را به نزدیکترین دفتر افغان اتصال بیاورید. ثبت نام اجباری است و به امنیت شبکه کمک می کند.",
                    "ثبت سیم به تذکره اصلی شما نیاز دارد. به هر یک از مراکز خدمات ما مراجعه کنید - ما در تمام شهرهای بزرگ مراکز داریم. این فرآیند سریع و رایگان است."
                ],
                'technical': [
                    "برای مشکلات شبکه، این مراحل را امتحان کنید: 1) دستگاه خود را restart کنید 2) بررسی کنید که در منطقه تحت پوشش هستید 3) مطمئن شوید که دیتا فعال است 4) انتخاب دستی شبکه را امتحان کنید. اگر مشکلات ادامه داشت، به مرکز خدمات ما مراجعه کنید.",
                    "عیب یابی معمول: تلفن خود را restart کنید، قرارگیری سیم کارت را بررسی کنید، مطمئن شوید که دیتای موبایل فعال است، و تأیید کنید که پوشش شبکه دارید. برای مشکلات مداوم، با پشتیبانی فنی در 0799000000 تماس بگیرید.",
                    "اگر مشکلات شبکه دارید: 1) دستگاه خود را restart کنید 2) پوشش در منطقه خود را بررسی کنید 3) تأیید کنید که سیم شما به درستی inserted شده 4) مطمئن شوید که بیلانس فعال دارید. برای کمک بیشتر؟ با 0799000000 تماس بگیرید."
                ],
                'default': [
                    "از سوال شما متشکریم. من اینجا هستم تا در مورد خدمات افغان اتصال از جمله بررسی بیلانس، بسته های اینترنتی، پوشش شبکه، ثبت سیم و پشتیبانی فنی کمک کنم. برای کمک دقیق تر، می توانید با خدمات مشتریان ما در 0799000000 تماس بگیرید.",
                    "منظور شما را متوجه شدم. من می توانم با خدمات مختلف افغان اتصال کمک کنم. لطفاً جزئیات بیشتری در مورد آنچه نیاز به کمک دارید ارائه دهید؟",
                    "من اینجا هستم تا در مورد خدمات افغان اتصال به شما کمک کنم. خواه در مورد بیلانس، بسته های اینترنتی، پوشش شبکه، یا مسائل فنی باشد، من آماده کمک هستم. همچنین می توانید با تیم پشتیبانی ما در 0799000000 تماس بگیرید."
                ]
            },
            'ps': {
                'greeting': [
                    "سلام! د افغان اتصال د AI ملاتړ ته ښه راغلئ. زه کولی شم تاسو سره د بیلانس چک، انټرنیټ پیکیجونو، د شبکې پوښښ، د سیم ثبت او تخنیکي ملاتړ په اړه مرسته وکړم. زه نن څنګه تاسو سره مرسته کولی شم؟",
                    "سلام! د افغان اتصال د پیرودونکو ملاتړ سره د تاسو د اړیکې لپاره مننه. زه نن څنګه تاسو سره مرسته کولی شم؟",
                    "سلام! افغان اتصال ته ښه راغلئ. زه ستاسو د AI مرستیال یم. زه څنګه کولی شم د زموږ د خدماتو په اړه تاسو سره مرسته وکړم؟"
                ],
                'balance': [
                    "تاسې کولی شئ د خپل د افغان اتصال شمیرې څخه د *123# په ډایل کولو سره خپل بیلانس وګورئ. ستاسې اوسنی بیلانس او اعتبار به فوراً ښکاره شي.",
                    "د بیلانس د چک لپاره، یوازې *123# ډایل کړئ. تاسو به خپل اصلي بیلانس، ډیټا بیلانس او هر فعال پیکیج وګورئ.",
                    "د بیلانس پوښتنې لپاره، د خپل افغان اتصال سیم څخه *123# ډایل کړئ. تاسو کولی شئ د MyConnect موبایل اپلیکیشن هم وکاروئ."
                ],
                'package': [
                    "موږ څو انټرنیټ پیکیجونه وړاندې کوو:\n- اساسي: 100 افغانۍ - 1 گیګابایټ د 7 ورځو لپاره\n- معیاري: 200 افغانۍ - 3 گیګابایټ د 15 ورځو لپاره\n- پریمیوم: 500 افغانۍ - 10 گیګابایټ د 30 ورځو لپاره\n- سوپر: 800 افغانۍ - 20 گیګابایټ د 30 ورځو لپاره\n\nد ګډون لپاره، *123*1# ډایل کړئ او لارښوونې تعقیب کړئ.",
                    "شته انټرنیټ پیکیجونه:\n- اساسي (1 گیګابایټ/7 ورځې): 100 افغانۍ\n- معیاري (3 گیګابایټ/15 ورځې): 200 افغانۍ\n- پریمیوم (10 گیګابایټ/30 ورځې): 500 افغانۍ\n- سوپر (20 گیګابایټ/30 ورځې): 800 افغانۍ\n\nد هر پیکیج د ګډون لپاره، *123*1# ډایل کړئ."
                ],
                'coverage': [
                    "افغان اتصال په ټولو 34 ولایتونو کې پراخ پوښښ لري د قوي 4G سګنالونو سره په ښاري سیمو کې او باور وړ پوښښ په کلیوالي سیمو کې. زموږ شبکه د 90٪ څخه زیاده اوسیدونکو سیمو پوښي.",
                    "موږ د ملي پوښښ سره د سګنال د عالي کیفیت سره په کابل، هرات، مزارشریف، قندهار، جلال آباد، کندز او نورو لویو ښارونو کې چمتو کوو. پوښښ په دوامداره توګه غځیږي.",
                    "زموږ شبکه ټول لوی ښارونه او ډیری کلیوالي سیمې پوښي. تاسو کولی شئ په خپل سیمه کې مشخص پوښښ وګورئ د زموږ ویب پاڼې ته د لیدلو یا د شبکې معلوماتو لپاره *123# ډایل کولو سره."
                ],
                'sim': [
                    "د سیم ثبت لپاره، مهرباني وکړئ د خپل اصلي تذکرې ID کارت سره د افغان اتصال د خدمت مرکز ته مراجعه وکړئ. دا پروسه نږدې 15-20 دقیقې وخت نیسي او په بشپړ ډول وړیا ده.",
                    "د خپل سیم کارت د ثبت لپاره، خپل اصلي تذکره نږدې افغان اتصال دفتر ته راوړئ. ثبت اجباري دی او د شبکې امنیت سره مرسته کوي.",
                    "د سیم ثبت ستاسو د اصلي تذکرې ته اړتیا لري. د زموږ د خدمت د مرکزونو څخه هر یو ته مراجعه وکړئ - موږ په ټولو لویو ښارونو کې مراکز لرو. دا پروسه ګړنده او وړیا ده."
                ],
                'technical': [
                    "د شبکې ستونزو لپاره، دا ګامونه هڅه وکړئ: 1) خپل وسیله ریسټارټ کړئ 2) وګورئ چې تاسو په پوښښ سیمه کې یاست 3) ډاډه اوسئ چې ډیټا فعال دی 4) د لاسي شبکې انتخاب هڅه وکړئ. که ستونزې دوام ولري، زموږ د خدمت مرکز ته مراجعه وکړئ.",
                    "عمومي حل: خپل تلیفون ریسټارټ کړئ، د سیم کارت ځای په ځای کول وګورئ، ډاډه اوسئ چې موبایل ډیټا فعال دی، او تایید کړئ چې تاسو د شبکې پوښښ لرئ. د دوامدارو ستونزو لپاره، په 0799000000 کې د تخنیکي ملاتړ سره اړیکه ونیسئ.",
                    "که تاسو د شبکې ستونزې تجربه کوئ: 1) خپل وسیله ریسټارټ کړئ 2) په خپل سیمه کې پوښښ وګورئ 3) تایید کړئ چې ستاسو سیم په سمه توګه inserted دی 4) ډاډه اوسئ چې تاسو فعال بیلانس لرئ. نوره مرسته غواړئ؟ په 0799000000 کې زنګ ووهئ."
                ],
                'default': [
                    "ستاسو د پوښتنې لپاره مننه. زه دلته یم چې د افغان اتصال خدماتو سره مرسته وکړم پکې د بیلانس چک، انټرنیټ پیکیجونه، د شبکې پوښښ، د سیم ثبت او تخنیکي ملاتړ شامل دي. د دقیقې مرستې لپاره، تاسو کولی شئ زموږ د پیرودونکو خدمت سره په 0799000000 کې اړیکه ونیسئ.",
                    "زه ستاسو مطلب پوهیږم. زه کولی شم د مختلفو افغان اتصال خدماتو سره مرسته وکړم. مهرباني وکړئ نور توضیحات راکړئ چې تاسو څه مرسته غواړئ؟",
                    "زه دلته یم چې تاسو سره د افغان اتصال خدماتو په اړه مرسته وکړم. که دا د بیلانس، انټرنیټ پیکیجونو، د شبکې پوښښ، یا تخنیکي مسلو په اړه وي، زه د مرستې لپاره چمتو یم. تاسو کولی شئ زموږ د ملاتړ ټیم سره په 0799000000 کې هم اړیکه ونیسئ."
                ]
            }
        }

        lang_responses = responses.get(language, responses['en'])
        category_responses = lang_responses.get(intent, lang_responses['default'])
        return random.choice(category_responses)
