"""
Management command to seed the database with initial telecom data.
Run with: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from ai_agent.models import (
    TelecomKnowledgeBase, InternetPackage, CoverageArea, TechnicalSupportFAQ
)


class Command(BaseCommand):
    help = 'Seed the database with initial telecom data for RAG'

    def handle(self, *args, **options):
        self._seed_knowledge_base()
        self._seed_packages()
        self._seed_coverage()
        self._seed_faqs()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def _seed_knowledge_base(self):
        entries = [
            {
                'category': 'balance',
                'question_en': 'How do I check my balance?',
                'question_dari': 'چگونه بیلانس خود را چک کنم؟',
                'question_pashto': 'زه خپل بیلانس څنګه وګورم؟',
                'answer_en': 'You can check your balance by dialing *123# from your Afghan Connect number. Your current balance and validity will be displayed immediately. You can also check your balance through the MyConnect mobile app available on Google Play and App Store.',
                'answer_dari': 'شما می‌توانید با شماره‌گیری *123# از شماره افغان اتصال خود، بیلانس خود را بررسی کنید. همچنین می‌توانید از اپلیکیشن MyConnect استفاده کنید.',
                'answer_pashto': 'تاسو کولی شئ د خپل افغان اتصال شمیرې څخه د *123# په ډایل کولو سره خپل بیلانس وګورئ. تاسو کولی شئ د MyConnect اپلیکیشن هم وکاروئ.',
            },
            {
                'category': 'balance',
                'question_en': 'How can I recharge my account?',
                'question_dari': 'چگونه می توانم حساب خود را شارژ کنم؟',
                'question_pashto': 'زه خپل حساب څنګه چارج کړم؟',
                'answer_en': 'You can recharge your Afghan Connect account by purchasing a scratch card from any authorized retailer and dialing *123*[PIN]#. You can also recharge online through the MyConnect app or via mobile banking services.',
                'answer_dari': 'شما می‌توانید حساب افغان اتصال خود را با خرید کارت شارژ از هر فروشنده مجاز و شماره‌گیری *123*[PIN]# شارژ کنید.',
                'answer_pashto': 'تاسو کولی شئ د خپل افغان اتصال حساب د هر مجاز پلورونکي څخه د سکریچ کارت پیرودلو او *123*[PIN]# په ډایل کولو سره چارج کړئ.',
            },
            {
                'category': 'sim',
                'question_en': 'What documents do I need for SIM registration?',
                'question_dari': 'برای ثبت سیم کارت چه مدارکی نیاز دارم؟',
                'question_pashto': 'د سیم کارت ثبت لپاره کوم اسنادو ته اړتیا لرم؟',
                'answer_en': 'For SIM registration, you need your original Tazkira (Afghan national ID card). If you are a foreigner, you need your passport with a valid visa. Visit any Afghan Connect service center - the process takes about 15-20 minutes and is completely free.',
                'answer_dari': 'برای ثبت سیم کارت، به تذکره اصلی خود نیاز دارید. اگر خارجی هستید، به پاسپورت با ویزای معتبر نیاز دارید. به هر مرکز خدمات افغان اتصال مراجعه کنید.',
                'answer_pashto': 'د سیم کارت ثبت لپاره، تاسو خپل اصلي تذکرې ته اړتیا لرئ. که تاسو بهرنی یاست، تاسو د اعتباري ویزې سره پاسپورټ ته اړتیا لرئ.',
            },
            {
                'category': 'technical',
                'question_en': 'My internet is not working, what should I do?',
                'question_dari': 'اینترنت من کار نمی کند، چه کار کنم؟',
                'question_pashto': 'زما انټرنیټ کار نه کوي، څه وکړم؟',
                'answer_en': 'If your internet is not working, try these steps: 1) Restart your device 2) Toggle Airplane Mode on/off 3) Check if mobile data is enabled 4) Ensure you have sufficient balance or an active data package 5) Try manual network selection. If the issue persists, contact our support at 0799000000.',
                'answer_dari': 'اگر اینترنت شما کار نمی کند، این مراحل را امتحان کنید: 1) دستگاه خود را restart کنید 2) حالت هواپیما را روشن/خاموش کنید 3) مطمئن شوید دیتای موبایل فعال است 4) از بیلانس کافی یا بسته دیتای فعال اطمینان حاصل کنید.',
                'answer_pashto': 'که ستاسو انټرنیټ کار نه کوي، دا ګامونه هڅه وکړئ: 1) خپل وسیله ریسټارټ کړئ 2) د الوتکې حالت آن/آف کړئ 3) ډاډه اوسئ چې موبایل ډیټا فعال دی 4) ډاډه اوسئ چې تاسو کافي بیلانس یا فعال ډیټا پیکیج لرئ.',
            },
            {
                'category': 'coverage',
                'question_en': 'Which cities have 4G coverage?',
                'question_dari': 'کدام شهرها پوشش 4G دارند؟',
                'question_pashto': 'کوم ښارونه د 4G پوښښ لري؟',
                'answer_en': 'Afghan Connect provides 4G coverage in all major cities including Kabul, Herat, Mazar-i-Sharif, Kandahar, Jalalabad, Kunduz, Balkh, Nangarhar, Ghazni, and many more. Our 4G network covers over 90% of populated areas. Coverage is continuously expanding to rural areas.',
                'answer_dari': 'افغان اتصال پوشش 4G را در تمام شهرهای بزرگ از جمله کابل، هرات، مزارشریف، قندهار، جلال آباد، کندز، بلخ، ننگرهار، غزنی و بسیاری دیگر فراهم می کند.',
                'answer_pashto': 'افغان اتصال په ټولو لویو ښارونو کې د 4G پوښښ چمتو کوي پکې کابل، هرات، مزارشریف، قندهار، جلال آباد، کندز، بلخ، ننگرهار، غزني او نور ډیر شامل دي.',
            },
        ]
        for entry in entries:
            TelecomKnowledgeBase.objects.get_or_create(
                question_en=entry['question_en'],
                defaults=entry
            )
        self.stdout.write(f'  Seeded {len(entries)} knowledge base entries')

    def _seed_packages(self):
        packages = [
            {
                'name_en': 'Basic Data',
                'name_dari': 'دیتای پایه',
                'name_pashto': 'اساسي ډیټا',
                'price_afn': 100,
                'data_amount': '1 GB',
                'validity_days': 7,
                'description_en': 'Perfect for light browsing and messaging',
                'description_dari': 'مناسب برای مرور سبک و پیام رسانی',
                'description_pashto': 'د لږ لټون او پیغام رسولو لپاره مناسب',
                'activation_code': '*123*1*1#',
                'is_active': True,
            },
            {
                'name_en': 'Standard Data',
                'name_dari': 'دیتای استاندارد',
                'name_pashto': 'معیاري ډیټا',
                'price_afn': 200,
                'data_amount': '3 GB',
                'validity_days': 15,
                'description_en': 'Great for social media and daily use',
                'description_dari': 'عالی برای شبکه های اجتماعی و استفاده روزانه',
                'description_pashto': 'د ټولنیزو رسنیو او ورځني استعمال لپاره غوره',
                'activation_code': '*123*1*2#',
                'is_active': True,
            },
            {
                'name_en': 'Premium Data',
                'name_dari': 'دیتای پریمیوم',
                'name_pashto': 'پریمیوم ډیټا',
                'price_afn': 500,
                'data_amount': '10 GB',
                'validity_days': 30,
                'description_en': 'Ideal for streaming and heavy usage',
                'description_dari': 'ایده آل برای استریمینگ و استفاده سنگین',
                'description_pashto': 'د سټریمینګ او درنې استعمال لپاره مناسب',
                'activation_code': '*123*1*3#',
                'is_active': True,
            },
            {
                'name_en': 'Super Data',
                'name_dari': 'دیتای سوپر',
                'name_pashto': 'سوپر ډیټا',
                'price_afn': 800,
                'data_amount': '20 GB',
                'validity_days': 30,
                'description_en': 'Maximum data for power users',
                'description_dari': 'حداکثر دیتا برای کاربران حرفه ای',
                'description_pashto': 'د پیاوړو کاروونکو لپاره اعظمي ډیټا',
                'activation_code': '*123*1*4#',
                'is_active': True,
            },
            {
                'name_en': 'Night Data',
                'name_dari': 'دیتای شب',
                'name_pashto': 'د شپې ډیټا',
                'price_afn': 150,
                'data_amount': '5 GB',
                'validity_days': 7,
                'description_en': '5GB data valid from 12AM to 7AM',
                'description_dari': '5 گیگابایت دیتا معتبر از 12 شب تا 7 صبح',
                'description_pashto': '5 GB ډیټا د شپې له 12 څخه تر 7 پورې اعتبار لري',
                'activation_code': '*123*1*5#',
                'is_active': True,
            },
        ]
        for pkg in packages:
            InternetPackage.objects.get_or_create(
                name_en=pkg['name_en'],
                defaults=pkg
            )
        self.stdout.write(f'  Seeded {len(packages)} internet packages')

    def _seed_coverage(self):
        areas = [
            {'province': 'Kabul', 'city': 'Kabul City', 'coverage_type': '4g', 'status': 'active', 'notes_en': 'Full 4G coverage in all districts'},
            {'province': 'Kabul', 'city': 'Paghman', 'coverage_type': '4g', 'status': 'active', 'notes_en': 'Good coverage'},
            {'province': 'Herat', 'city': 'Herat City', 'coverage_type': '4g', 'status': 'active', 'notes_en': 'Full 4G coverage'},
            {'province': 'Herat', 'city': 'Islam Qala', 'coverage_type': '3g', 'status': 'active', 'notes_en': '3G coverage available'},
            {'province': 'Balkh', 'city': 'Mazar-i-Sharif', 'coverage_type': '4g', 'status': 'active', 'notes_en': 'Full 4G coverage'},
            {'province': 'Kandahar', 'city': 'Kandahar City', 'coverage_type': '4g', 'status': 'active', 'notes_en': '4G coverage in urban areas'},
            {'province': 'Nangarhar', 'city': 'Jalalabad', 'coverage_type': '4g', 'status': 'active', 'notes_en': 'Strong 4G signal'},
            {'province': 'Kunduz', 'city': 'Kunduz City', 'coverage_type': '4g', 'status': 'active', 'notes_en': '4G active'},
            {'province': 'Ghazni', 'city': 'Ghazni City', 'coverage_type': '3g', 'status': 'active', 'notes_en': '3G coverage, 4G planned'},
            {'province': 'Bamyan', 'city': 'Bamyan City', 'coverage_type': '3g', 'status': 'active', 'notes_en': '3G available'},
            {'province': 'Samangan', 'city': 'Samangan City', 'coverage_type': '3g', 'status': 'planned', 'notes_en': 'Coverage expansion planned for 2025'},
            {'province': 'Badakhshan', 'city': 'Fayzabad', 'coverage_type': '3g', 'status': 'active', 'notes_en': '3G coverage'},
        ]
        for area in areas:
            CoverageArea.objects.get_or_create(
                province=area['province'],
                city=area['city'],
                coverage_type=area['coverage_type'],
                defaults=area
            )
        self.stdout.write(f'  Seeded {len(areas)} coverage areas')

    def _seed_faqs(self):
        faqs = [
            {
                'category': 'network',
                'question_en': 'Why is my call quality poor?',
                'question_dari': 'چرا کیفیت تماس من ضعیف است؟',
                'question_pashto': 'ولې زما د زنګ کیفیت خراب دی؟',
                'answer_en': 'Poor call quality can be caused by: 1) Weak network signal - try moving to an open area 2) Network congestion during peak hours 3) Damaged SIM card - visit a service center for a free replacement 4) Device issues - try restarting your phone. If the problem persists, contact our support at 0799000000.',
                'answer_dari': 'کیفیت پایین تماس می تواند ناشی از: 1) سیگنال ضعیف شبکه 2) ازدحام شبکه در ساعات اوج 3) سیم کارت آسیب دیده 4) مشکلات دستگاه باشد.',
                'answer_pashto': 'د زنګ خراب کیفیت د دې له امله کیدی شي: 1) ضعیف د شبکې سیګنال 2) د شبکې ګڼه ګوڼه 3) خراب سیم کارت 4) د وسیلې ستونزې.',
            },
            {
                'category': 'device',
                'question_en': 'How do I configure APN settings for mobile internet?',
                'question_dari': 'چگونه تنظیمات APN را برای اینترنت موبایل پیکربندی کنم؟',
                'question_pashto': 'د موبایل انټرنیټ لپاره د APN ترتیبات څنګه ترتیب کړم؟',
                'answer_en': 'To configure APN settings: Go to Settings > Mobile Networks > Access Point Names. Create a new APN with: Name: Afghan Connect, APN: afghanconnect.net, Username: (leave blank), Password: (leave blank), MCC: 412, MNC: 01. Save and select this APN. Restart your device if needed.',
                'answer_dari': 'برای تنظیم APN: به تنظیمات > شبکه های موبایل > نام نقاط دسترسی بروید. یک APN جدید با: نام: Afghan Connect، APN: afghanconnect.net ایجاد کنید.',
                'answer_pashto': 'د APN تنظیم لپاره: ترتیبات > موبایل شبکې > د لاسرسي نقطو نومونو ته لاړ شئ. د: نوم: Afghan Connect، APN: afghanconnect.net سره نوې APN جوړه کړئ.',
            },
            {
                'category': 'billing',
                'question_en': 'How do I get a detailed bill?',
                'question_dari': 'چگونه صورت حساب دقیق دریافت کنم؟',
                'question_pashto': 'زه څنګه مفصل بل ترلاسه کړم؟',
                'answer_en': 'You can get a detailed bill by: 1) Dialing *123# for a summary 2) Downloading the MyConnect app for detailed usage history 3) Visiting any Afghan Connect service center 4) Calling our customer service at 0799000000. Detailed bills are available for the last 3 months.',
                'answer_dari': 'شما می‌توانید صورت حساب دقیق را با: 1) شماره‌گیری *123# 2) دانلود اپلیکیشن MyConnect 3) مراجعه به مرکز خدمات 4) تماس با 0799000000 دریافت کنید.',
                'answer_pashto': 'تاسو کولی شئ مفصل بل د: 1) *123# په ډایل کولو 2) د MyConnect اپلیکیشن ډاونلوډ 3) د خدمت مرکز ته لیدنه 4) په 0799000000 کې زنګ وهلو سره ترلاسه کړئ.',
            },
            {
                'category': 'account',
                'question_en': 'How can I change my language preference?',
                'question_dari': 'چگونه می توانم زبان ترجیحی خود را تغییر دهم؟',
                'question_pashto': 'زه خپله ژبه څنګه بدل کړم؟',
                'answer_en': 'You can change your language preference in the MyConnect app settings. We support English, Dari, and Pashto. You can also change the language by dialing *123# and selecting option 9 for settings, then choose your preferred language.',
                'answer_dari': 'شما می‌توانید زبان ترجیحی خود را در تنظیمات اپلیکیشن MyConnect تغییر دهید. ما از انگلیسی، دری و پشتو پشتیبانی می کنیم.',
                'answer_pashto': 'تاسو کولی شئ د MyConnect اپلیکیشن ترتیباتو کې خپله ژبه بدله کړئ. موږ د انګلیسي، دري او پښتو ملاتړ کوو.',
            },
            {
                'category': 'network',
                'question_en': 'How do I activate VoLTE?',
                'question_dari': 'چگونه VoLTE را فعال کنم؟',
                'question_pashto': 'زه VoLTE څنګه فعال کړم؟',
                'answer_en': 'To activate VoLTE (HD Voice): 1) Ensure your device supports VoLTE 2) Go to Settings > Mobile Networks > VoLTE/Voice over LTE 3) Toggle VoLTE on. If you don\'t see this option, your device may not support VoLTE. VoLTE provides clearer voice calls and faster call setup.',
                'answer_dari': 'برای فعال کردن VoLTE: 1) مطمئن شوید دستگاه شما از VoLTE پشتیبانی می کند 2) به تنظیمات > شبکه های موبایل > VoLTE بروید 3) VoLTE را روشن کنید.',
                'answer_pashto': 'د VoLTE فعالولو لپاره: 1) ډاډه اوسئ چې ستاسو وسیله د VoLTE ملاتړ کوي 2) ترتیبات > موبایل شبکې > VoLTE ته لاړ شئ 3) VoLTE فعال کړئ.',
            },
        ]
        for faq in faqs:
            TechnicalSupportFAQ.objects.get_or_create(
                question_en=faq['question_en'],
                defaults=faq
            )
        self.stdout.write(f'  Seeded {len(faqs)} technical support FAQs')
