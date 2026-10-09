# ۱۱. بکاپ، بازیابی و ارتقا

[فهرست](README.md)

## چه چیزی باید حفظ شود؟

- دیتابیس کاربران/مصرف/تنظیمات.
- Volume کامل: state نصب، کلید و گواهی نود، REALITY keys در صورت فعال‌بودن و سایر داده‌های پایه.
- فایل `.env` خصوصی و نسخهٔ دقیق image/source؛ `.env` را در مخزن عمومی نگه ندار.
- Volumeهای Caddy برای گواهی/حساب ACME؛ بازیابی کلیدها حساس است.

نسخهٔ کپی‌شده از دیتابیس روی همان سرور، بکاپ برون‌سایتی یا رمزگذاری‌شده نیست. retention و فضای دیسک را خودت تعیین کن؛ ابزار فعلی بکاپ زمان‌بندی‌شده ندارد.

## بکاپ سازگار SQLite بدون توقف

```sh
umask 077
mkdir -p backups
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
docker compose -f compose.yaml -f compose.vps.yaml exec -T panel   python -m sabi_ray.backup --output /var/lib/pasarguard/backups/db-$STAMP.sqlite3
CID=$(docker compose -f compose.yaml -f compose.vps.yaml ps -q panel)
docker cp "$CID:/var/lib/pasarguard/backups/db-$STAMP.sqlite3" "backups/db-$STAMP.sqlite3"
chmod 600 "backups/db-$STAMP.sqlite3"
```

نام خروجی باید تازه باشد؛ ابزار فایل قبلی را overwrite نمی‌کند و integrity را بررسی می‌کند. این بکاپ فقط SQLite است؛ برای PostgreSQL/MySQL ابزار رسمی همان دیتابیس لازم است. از کپی خام یک SQLite در حال نوشتن به جای backup API استفاده نکن.

## بکاپ Volume در توقف کوتاه

در نصب direct فایل سوم Compose را به همهٔ دستورهای مربوط اضافه کن. قبل از توقف، شناسه را بگیر:

```sh
umask 077
mkdir -p backups
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
CID=$(docker compose -f compose.yaml -f compose.vps.yaml ps -q panel)
docker compose -f compose.yaml -f compose.vps.yaml stop panel
docker cp "$CID:/var/lib/pasarguard" "backups/volume-$STAMP"
docker compose -f compose.yaml -f compose.vps.yaml start panel
chmod -R go-rwx "backups/volume-$STAMP"
```

این کار احتمال قطعی کوتاه دارد. از بکاپ Volume روی همان مسیر production تست بازیابی نکن. آرشیو را خارج سرور، رمزگذاری‌شده و با دسترسی محدود نگه دار. آن را به Actions artifact عمومی، issue یا release پیوست نکن.

## تمرین بازیابی امن

۱. روی میزبان آزمایشی جدا، همان release و همان env غیرحساس را آماده کن. دسترسی خروجی نودهای production را مسدود کن؛ clone نباید به نودهای زنده متصل شود.
۲. یک پروژه/Volume جدید بساز؛ روی Volume فعال restore نکن.
۳. پیش از اولین start، کانتینر خام ایجاد و کپی Volume خصوصی را در `/var/lib/pasarguard` برگردان؛ مالکیت و permission فایل‌ها را حفظ کن.
۴. domain/profile state باید با env یکسان باشد؛ برای تست لازم نیست DNS عمومی production را عوض کنی. با hosts محلی/محیط ایزوله و TLS مناسب تست کن.
۵. راه‌اندازی، ورود، تعداد کاربران، سهمیه و پایداری کلیدهای اتصال را بررسی کن.
۶. فقط وقتی تمرین موفق است، سناریوی بازگشت عملیاتی را مستند کن.

### نمونهٔ ساخت مقصد بازیابی بدون overwrite روی production

فقط روی میزبان آزمایشیِ جدا و ایزوله، از ریشهٔ release متناظر بکاپ:

```sh
# .env خصوصی همان نصب و image متناظر را از قبل آماده کن.
# SOURCE را به پوشهٔ کامل بکاپی که خودت بررسی کردی تغییر بده.
SOURCE=/secure-backups/volume-YYYYMMDDTHHMMSSZ
[ -f "$SOURCE/db.sqlite3" ] || exit 1
[ -f "$SOURCE/sabi-installation.json" ] || exit 1
docker compose -p sabi-restore-check -f compose.yaml create panel
RESTORE_CID=$(docker compose -p sabi-restore-check -f compose.yaml ps -a -q panel)
[ -n "$RESTORE_CID" ] || exit 1
docker cp "$SOURCE/." "$RESTORE_CID:/var/lib/pasarguard/"
```

این دستور فقط مقصد **تازه**ٔ پروژهٔ sabi-restore-check را آماده می‌کند؛ اگر آن پروژه قبلاً داده دارد، توقف کن و مقصد جدید انتخاب کن. هیچ start خودکار در مثال نیست. قبل از start، شبکهٔ ایزوله و جلوگیری از اتصال به نودهای production را خودت برقرار کن. برای نصب خارجی با PostgreSQL این مثال معتبر نیست؛ dump/restore همان دیتابیس لازم است. تست داخل محیط ایزوله با همان مشخصات domain/state انجام شود و نتیجهٔ شمارش کاربران و ورود ثبت شود.

این فصل یک runbook است، نه ادعای انجام تمرین بازیابی روی سرور تو.

## ارتقا

۱. یادداشت release و گزارش CI را بخوان؛ اگر migration اعلام نشده، بی‌وقفه فرض نکن.
۲. بکاپ کامل و مشخصات نسخهٔ فعلی را نگه دار.
۳. روی clone ایزوله تست کن.
۴. زمان نگهداری و احتمال قطعی را مشخص کن.

```sh
git status --short
git fetch --tags
git checkout v0.2.0-alpha.2
docker compose -f compose.yaml -f compose.vps.yaml up -d --build
docker compose -f compose.yaml -f compose.vps.yaml ps
```

روی تغییرات محلی `reset --hard` نزن. نسخهٔ 0.1 با advanced غیرفعال از نظر state پشتیبانی می‌شود، اما افزودن advanced یا تغییر domain/profile روی نصب موجود نیازمند مهاجرت صریح است و فعلاً ابزار آن نداریم.

## بازگشت

قدیمی‌کردن image به‌تنهایی بعد از migration دیتابیس کافی نیست. image و Volume/DB متناظر همان زمان را با هم برگردان. این کار دادهٔ جدید بعد از بکاپ را ممکن است از دست بدهد؛ قبلش تصمیم و ثبت لازم است. `down -v` هیچ‌وقت فرمان عادی ارتقا نیست.
