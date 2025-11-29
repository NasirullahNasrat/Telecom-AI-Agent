import openai
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class TelecomAIService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.supported_languages = ['en', 'fa', 'ps']
    
    def get_system_prompt(self, language):
        prompts = {
            'en': """You are a helpful AI customer support agent for Afghan Connect, Afghanistan's first Connect communications company.

Key Information:
- First Connect company in Afghanistan (since 2002)
- Offers HD Voice, Internet, Data, and Mobile Payments
- Over 6,000 employees

Common Telecom Queries:
1. Balance Checking: Guide to dial *123# or use mobile app
2. Internet Packages: Basic: 100AFN/1GB, Standard: 200AFN/3GB, Premium: 500AFN/10GB
3. SIM Registration: Visit nearest Connect office with Tazkira ID
4. Network Coverage: Available in all major cities
5. Technical Support: Basic troubleshooting

Guidelines:
- Be concise and helpful
- Provide accurate information
- If unsure, direct to human support at 0799000000
- Always be polite and patient""",

            'fa': """شما یک دستیار هوش مصنوعی پشتیبانی مشتریان برای شرکت افغان اتصال هستید.

اطلاعات کلیدی:
- اولین شرکت بی سیم در افغانستان (از سال 2002)
- ارائه دهنده خدمات صدا HD، اینترنت، دیتا و پرداخت های موبایل
- بیش از 6,000 کارمند

پرسش های متداول:
1. بررسی بیلانس: راهنمایی برای شماره گیری *123# یا استفاده از اپلیکیشن
2. بسته های اینترنتی: پایه: 100 افغانی/1 گیگابایت، استاندارد: 200 افغانی/3 گیگابایت
3. ثبت سیم: مراجعه به دفتر نزدیک Connect با تذکره
4. پوشش شبکه: در تمام شهرهای بزرگ موجود
5. پشتیبانی فنی: عیب یابی اولیه

دستورالعمل ها:
- مختصر و مفید باشید
- اطلاعات دقیق ارائه دهید
- اگر مطمئن نیستید، به پشتیبانی انسانی در 0799000000 ارجاع دهید""",

            'ps': """تاسې د افغان اتصال لپاره د مصنوعي ذکاء مرستیال یاست.

مهم معلومات:
- د افغانستان لومړی بې سيمه شرکت (له ۲۰۰۲ راهیسې)
- د HD غږ، انټرنیټ، ډیټا او موبایل پیسې خدمتونه
- له 6,000 څخه زیات کارکوونکي

عمومي پوښتنې:
1. د بیلانس چک: د *123# ډایل کولو لارښود
2. د انټرنیټ پیکیجونه: اساسي: 100 افغانۍ/1 گیګابایټ، معیاري: 200 افغانۍ/3 گیګابایټ
3. د سیم ثبت: د تذکرې سره نږدې Connect دفتر ته مراجعه
4. د شبکې پوښښ: په ټولو لویو ښارونو کې
5. تخنیکي ملاتړ: لومړنی حل

لارښوونې:
- لنډ او مرستندویه اوسئ
- دقیق معلومات وړاندې کړئ
- که ډاډه نه یاست، په 0799000000 کې ملاتړ ته ورګرځئ"""
        }
        return prompts.get(language, prompts['en'])
    
    def generate_response(self, message, language='en'):
        try:
            system_prompt = self.get_system_prompt(language)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self.get_fallback_response(language)
    
    def get_fallback_response(self, language):
        fallbacks = {
            'en': "I apologize, but I'm having trouble processing your request. Please try again or contact our support team at 0799000000.",
            'fa': "عذر میخواهم، در پردازش درخواست شما مشکل دارم. لطفاً دوباره تلاش کنید یا با تیم پشتیبانی ما در 0799000000 تماس بگیرید.",
            'ps': "بخښنه غواړم، زه ستاسو د غوښتنې په پروسس کې مشکل لرم. مهرباني وکړئ بیا هڅه وکړئ یا زموږ د ملاتړ ټیم سره په 0799000000 کې اړیکه ونیسئ."
        }
        return fallbacks.get(language, fallbacks['en'])