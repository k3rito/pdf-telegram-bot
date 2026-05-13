# 🤖 بوت PDF على تيليجرام

بوت شامل لخدمات PDF يدعم:

| الخدمة | الوصف |
|--------|-------|
| 📎 دمج | دمج عدة ملفات PDF في ملف واحد |
| ✂️ تقسيم | تقسيم PDF إلى صفحات منفصلة |
| 🗜️ ضغط | تقليل حجم ملف PDF |
| 📝 استخراج نصوص | استخراج كل النصوص من PDF |
| 🖼️ استخراج صور | استخراج الصور من PDF |
| 🖼️➡️📄 صور إلى PDF | تحويل مجموعة صور إلى PDF |
| 📄➡️📝 PDF إلى Word | تحويل PDF إلى ملف .docx |
| 📊 PDF إلى Excel | استخراج الجداول إلى .xlsx |

---

## ⚙️ طريقة الإعداد

### 1. إنشاء البوت
1. افتح تيليجرام → ابحث عن **@BotFather**
2. أرسل `/newbot` واتبع التعليمات
3. انسخ **التوكن** الذي سيعطيك إياه

### 2. استنساخ المشروع
```bash
git clone https://github.com/your-username/pdf-bot.git
cd pdf-bot
```

### 3. إعداد ملف البيئة
```bash
cp .env.example .env
```
افتح ملف `.env` وضع توكنك:
```
BOT_TOKEN=123456:ABCdef...
```

### 4. تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### 5. تشغيل البوت
```bash
python bot.py
```

---

## 🐳 تشغيل بـ Docker

```bash
docker build -t pdf-bot .
docker run --env-file .env pdf-bot
```

---

## 📋 هيكل المشروع

```
pdf-bot/
├── bot.py           # الكود الرئيسي
├── requirements.txt # المكتبات المطلوبة
├── .env.example     # مثال على ملف البيئة
├── .gitignore       # ملفات مستبعدة من Git
└── README.md        # هذا الملف
```

---

## ⚠️ ملاحظات أمان
- **لا ترفع ملف `.env`** على GitHub أبداً
- `.gitignore` يحمي ملف `.env` تلقائياً
- استخدم دائماً `.env.example` كمرجع للإعداد
