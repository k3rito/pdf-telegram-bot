# 🤖 PDF Bot

بوت Telegram لمعالجة ملفات PDF ببنية إنتاجية تعتمد على `python-telegram-bot` async بالكامل، مع Queue حقيقي، جلسات معزولة، ولوحة إدارة داخل البوت، وتهيئة جاهزة للتوسع نحو PostgreSQL وRedis.

## طريقة النداء

البوت لا يرد على الرسائل العادية أو أوامر `/commands`. التفعيل الوحيد يكون عبر:

```text
@pdf merge
@pdf split
@pdf compress
@pdf help
```

يدعم ذلك داخل الخاص والجروبات والسوبرجروبات، مع جلسات منفصلة لكل مستخدم.

راجع أيضًا [ARCHITECTURE.md](ARCHITECTURE.md) للحصول على تفصيل كامل للبنية، ومسار التوجيه، والـ queue، والـ session isolation.

## الخدمات المدعومة

- `@pdf merge`
- `@pdf split`
- `@pdf compress`
- `@pdf extract`
- `@pdf rotate`
- `@pdf ocr`
- `@pdf encrypt`
- `@pdf decrypt`
- `@pdf images`
- `@pdf reorder`
- `@pdf watermark`
- `@pdf cancel`
- `@pdf queue`
- `@pdf settings`
- `@pdf lang`

## التشغيل السريع

```bash
pip install -r requirements.txt
python bot.py
```

أو انسخ ملف البيئة النموذجي أولًا:

```bash
copy .env.example .env
```

## المتغيرات البيئية

ضع القيم التالية في ملف `.env`:

```env
BOT_TOKEN=123456:ABCDEF
ADMIN_IDS=123456789,987654321
PREFIX_TOKEN=@pdf
OCR_ENABLED=false
DEFAULT_LANG=ar
RATE_LIMIT_COUNT=5
RATE_LIMIT_WINDOW=60
MAX_FILE_SIZE=52428800
MAX_FILES_PER_SESSION=20
MAX_TOTAL_SIZE=209715200
WORKER_COUNT=2
TASK_TIMEOUT=240
TASK_RETRIES=1
CLEANUP_INTERVAL=900
DB_PATH=database/pdfbot.db
TEMP_DIR=temp
STORAGE_DIR=storage
LOG_DIR=logs
LOG_LEVEL=INFO
```

يمكنك البدء من `.env.example` ثم تعديل القيم حسب بيئة النشر.

## Docker

```bash
docker compose up --build
```

أو:

```bash
docker build -t pdf-bot .
docker run --env-file .env pdf-bot
```

## OCR

يستخدم البوت `pytesseract` عند تفعيل OCR. صورة Docker تثبت:

- `tesseract-ocr`
- `tesseract-ocr-ara`

## الأمان والأداء

- Rate limiting لمنع السبام
- جلسات مؤقتة على القرص مع تنظيف تلقائي
- `asyncio.to_thread` للمهام الثقيلة
- Queue منفصل للمعالجة
- حماية من الملفات الضخمة والصيغ غير الصالحة
- OCR preprocessing عبر OpenCV عند التوفر
- بنية قابلة للترقية لاحقًا إلى Redis-backed queue وPostgreSQL persistence

## البنية

```text
bot.py
config.py
core/
handlers/
services/
workers/
middleware/
database/
repositories/
keyboards/
models/
storage/
temp/
logs/
utils/
tests/
```

## ملفات النشر

- `Dockerfile` مبني على Python 3.11
- `docker-compose.yml` للتشغيل المحلي أو شبه الإنتاجي
- `Procfile` لدعم منصات PaaS
- `.env.example` كنقطة بداية للإعدادات

## ملاحظات إنتاجية

- لا توجد handlers متزامنة للحركة الأساسية.
- كل العمليات الثقيلة يجب أن تبقى خارج event loop.
- مفاتيح الجلسات تعتمد على `(chat_id, user_id)` لضمان العزل.
- يفضل تشغيل OCR داخل Docker لضمان توفر Tesseract وملحقات اللغة.
