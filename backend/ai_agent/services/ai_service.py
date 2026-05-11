import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class TelecomAIService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.supported_languages = ['en', 'fa', 'ps']
        
        if not self.api_key:
            logger.warning("DeepSeek API key not configured - service will use fallback responses")
    
    def get_system_prompt(self, language, rag_context=None):
        """Generate a system prompt that includes RAG context for natural, ChatGPT-like responses."""
        
        base_prompts = {
            'en': """You are a friendly, conversational AI customer support agent for Afghan Connect, Afghanistan's first communications company. 

Your personality:
- Warm, helpful, and conversational - like a knowledgeable friend
- You explain things clearly and naturally, not like a robot
- You use natural language and vary your sentence structure
- You're patient and understanding with customers

Key Information:
- First communications company in Afghanistan (since 2002)
- Offers HD Voice, Internet, Data, and Mobile Payments
- Over 6,000 employees, created 100,000+ jobs
- Customer support: 0799000000 or Connect.af

Guidelines:
- Respond conversationally like ChatGPT - natural, flowing language
- NEVER use bullet points, numbered lists, or markdown formatting in your response
- Write in full, natural paragraphs
- If you have specific data from the context below, weave it naturally into your response
- If unsure about something, direct to customer support: 0799000000
- Always be polite, patient, and warm
- Keep responses concise but natural""",

            'fa': """شما یک دستیار هوش مصنوعی پشتیبانی مشتریان گرم و گفتگوگر برای شرکت افغان اتصال هستید، اولین شرکت ارتباطات در افغانستان.

شخصیت شما:
- گرم، مفید و گفتگوگر - مانند یک دوست آگاه
- مسائل را واضح و طبیعی توضیح می‌دهید، نه مانند ربات
- از زبان طبیعی استفاده می‌کنید
- با مشتریان صبور و فهمیده هستید

اطلاعات کلیدی:
- اولین شرکت ارتباطات در افغانستان (از سال 2002)
- ارائه دهنده خدمات صدا HD، اینترنت، دیتا و پرداخت های موبایل
- بیش از 6,000 کارمند
- پشتیبانی مشتریان: 0799000000

دستورالعمل ها:
- به صورت گفتگوگر پاسخ دهید مانند ChatGPT - زبان روان و طبیعی
- هرگز از لیست های شماره‌دار یا بولت پوینت استفاده نکنید
- در پاراگراف های کامل و طبیعی بنویسید
- اگر اطلاعات خاصی از متن زمینه دارید، آن را به طور طبیعی در پاسخ خود بگنجانید
- اگر مطمئن نیستید، به پشتیبانی مشتریان در 0799000000 ارجاع دهید
- همیشه مودب، صبور و گرم باشید""",

            'ps': """تاسې د افغان اتصال لپاره یو دوستانه، خبرو اترو مصنوعي ذکاء د پیرودونکو ملاتړ مرستیال یاست، د افغانستان لومړنی مخابراتي شرکت.

ستاسې شخصیت:
- ګرم، مرستندویه او خبرو اترو کوونکی - لکه یو پوه ملګری
- شیان په واضح او طبیعي توګه تشریح کوئ، د روبوټ په څیر نه
- تاسې طبیعي ژبه کاروئ
- تاسې د پیرودونکو سره صبر او پوهه لرئ

مهم معلومات:
- په افغانستان کې لومړنی مخابراتي شرکت (له ۲۰۰۲ راهیسې)
- د HD غږ، انټرنیټ، ډیټا او موبایل پیسې خدمتونه وړاندې کوي
- له 6,000 څخه زیات کارکوونکي
- د پیرودونکو ملاتړ: 0799000000

لارښوونې:
- د ChatGPT په څیر په خبرو اترو سره ځواب ورکړئ - روانه او طبیعي ژبه
- هیڅکله د نمبر لرونکو لیستونو یا نښو څخه کار مه اخلئ
- په بشپړو، طبیعي پراګرافونو کې ولیکئ
- که تاسې لاندې له متن څخه مشخص معلومات لرئ، په طبیعي توګه یې په خپل ځواب کې شامل کړئ
- که ډاډه نه یاست، په 0799000000 کې د پیرودونکو ملاتړ ته ورګرځئ
- تل مهربان، صبر کوونکی او ګرم اوسئ"""
        }
        
        prompt = base_prompts.get(language, base_prompts['en'])
        
        # Append RAG context if available
        if rag_context:
            if language == 'en':
                prompt += f"\n\nHere is the current data from our database that you should use to answer the customer's question. Weave this information naturally into your conversational response:\n\n{rag_context}"
            elif language == 'fa':
                prompt += f"\n\nدر زیر اطلاعات فعلی از دیتابیس ما است که باید برای پاسخ به سوال مشتری استفاده کنید. این اطلاعات را به طور طبیعی در پاسخ گفتگوگر خود بگنجانید:\n\n{rag_context}"
            elif language == 'ps':
                prompt += f"\n\nلاندې زموږ د ډیټابیس اوسني معلومات دي چې تاسې باید د پیرودونکي پوښتنې ته د ځواب ورکولو لپاره وکاروئ. دا معلومات په طبیعي توګه په خپل خبرو اترو ځواب کې شامل کړئ:\n\n{rag_context}"
        
        return prompt
    
    def generate_response(self, message, language='en', rag_context=None):
        """Generate a natural, conversational response using DeepSeek API with optional RAG context."""
        try:
            logger.info(f"AI Service generating response for: {message[:50]}... in {language}")
            
            system_prompt = self.get_system_prompt(language, rag_context)
            
            if not self.api_key or self.api_key == 'your-deepseek-api-key-here':
                logger.warning("No API key configured, using fallback response")
                return self.get_fallback_response(language, rag_context)
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.8,
                "max_tokens": 600,
                "stream": False
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data['choices'][0]['message']['content']
                logger.info(f"AI Response: {ai_response[:50]}...")
                return ai_response
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return self.get_fallback_response(language, rag_context)
                
        except requests.exceptions.Timeout:
            logger.error("DeepSeek API request timed out")
            return self.get_fallback_response(language, rag_context)
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API request failed: {e}")
            return self.get_fallback_response(language, rag_context)
        except Exception as e:
            logger.error(f"Unexpected error in AI service: {e}")
            return self.get_fallback_response(language, rag_context)
    
    def get_fallback_response(self, language, rag_context=None):
        """Generate a natural fallback response, optionally using RAG context."""
        if rag_context:
            # If we have RAG context but API failed, format it naturally
            if language == 'en':
                return f"I'd be happy to help you with that! Here's what I found:\n\n{rag_context}\n\nIs there anything else I can help you with?"
            elif language == 'fa':
                return f"خوشحالم که می‌توانم کمک کنم! اطلاعات زیر را پیدا کردم:\n\n{rag_context}\n\nآیا کار دیگری می‌توانم برای شما انجام دهم؟"
            elif language == 'ps':
                return f"زه خوشحال یم چې مرسته کولی شم! ما لاندې معلومات وموندل:\n\n{rag_context}\n\nآیا بل څه شته چې زه یې ستاسو سره مرسته وکړم؟"
        
        fallbacks = {
            'en': "I apologize, but I'm having trouble processing your request right now. Please try again in a moment, or feel free to contact our support team at 0799000000 for immediate assistance. They'll be happy to help you out!",
            'fa': "عذر میخواهم، در حال حاضر در پردازش درخواست شما مشکل دارم. لطفاً چند لحظه دیگر تلاش کنید، یا برای دریافت کمک فوری با تیم پشتیبانی ما در 0799000000 تماس بگیرید. آنها خوشحال خواهند شد که به شما کمک کنند!",
            'ps': "بخښنه غواړم، اوس مهال ستاسو د غوښتنې په پروسس کې ستونزه لرم. مهرباني وکړئ یو څه وروسته بیا هڅه وکړئ، یا زموږ د ملاتړ ټیم سره په 0799000000 کې اړیکه ونیسئ. دوی به خوشحاله وي چې ستاسو سره مرسته وکړي!"
        }
        return fallbacks.get(language, fallbacks['en'])
