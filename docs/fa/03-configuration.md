# ۳. تنظیمات و اسرار

[فهرست](README.md)

## جدول متغیرها

| متغیر | معنی / پیش‌فرض | زمان تغییر |
|---|---|---|
| PUBLIC_DOMAIN | دامنهٔ HTTPS پنل، بدون scheme یا پورت | قبل از نصب؛ تغییر بعدی نیازمند برنامهٔ مهاجرت |
| SABI_ADMIN_USER | مالک اولیه؛ owner | نصب اولیه؛ تغییر بعدی از پنل |
| SABI_INITIAL_PASSWORD | رمز قوی اولیه؛ بدون پیش‌فرض | فقط تا تکمیل setup |
| SABI_PROFILES | vless-ws,trojan-ws,vmess-ws | قبل از نصب؛ لیست بدون تکرار |
| SABI_CONTROL_ONLY | false؛ اگر true فقط پنل، بدون نود داخلی | پیش از نصب |
| SABI_ADVANCED | خالی؛ گزینه‌ها reality,shadowsocks | پیش از نصب |
| SABI_DIRECT_DOMAIN | دامنهٔ DNS-only برای پروتکل مستقیم | همراه advanced |
| SABI_REALITY_TARGET | میزبان TLS مجاز و پورت، مثلاً origin.example.com:443 | همراه reality |
| SABI_REALITY_SERVER_NAME | پیش‌فرض نام میزبان target | باید مطابق hostname هدف باشد |
| PORT | 8080 برای nginx | در Compose معمولی ثابت نگه دار؛ تغییر mapping/healthcheck هم لازم است |
| DEPLOY_MODE | docker / vps / railway | فایل Compose مربوطه آن را تعیین می‌کند |
| RAILWAY_APPROVAL_CONFIRMED | از 0.2.0-alpha.2 منسوخ و نادیده گرفته می‌شود | لازم نیست؛ حذف آن روی داده‌ها اثری ندارد. بررسی مقررات میزبان مستقل است |
| SQLALCHEMY_DATABASE_URL | SQLite روی Volume در Dockerfile | تغییر دیتابیس یک پروژهٔ مهاجرت مستقل است |

پروفایل‌های وب اختیاری `vless-upgrade` و `vless-xhttp` هستند. نصب control-only همچنان به دامنه و رمز نیاز دارد و با SABI_ADVANCED همزمان مجاز نیست.

## دامنه‌ها را قاطی نکن

- PUBLIC_DOMAIN: آدرس پنل/اشتراک و اتصال‌های وب.
- SABI_DIRECT_DOMAIN: رکورد مستقیم به همان VPS؛ پشت CDN معمولی قرار نده.
- REALITY target/SNI: سایت TLS مبدأ مجاز و سازگار؛ نه نشانی خود listener، نه کلید خصوصی.

## نقل‌قول و رمز در .env

Compose مقدارهای بدون نقل‌قول یا با double quote را ممکن است با `$` تفسیر کند. ابزار `scripts/init-env.py` از single quote استفاده می‌کند و کاراکترهای ناسازگار با این روش را رد می‌کند. فایل را با shell `source .env` نکن؛ این فایل برای Compose است. متغیرهای Railway از رابط Variables وارد می‌شوند، نه به شکل فرمان shell.

`docker inspect`، dump کامل `docker compose config`، فایل `.env`، لینک ساب، QR و محتوای Volume را اسرار حساب کن. `.gitignore` جلوی ارسال دستی یا ثبت در تاریخچهٔ قدیمی را نمی‌گیرد.

## چرا تغییر متغیر بعد از نصب خطا می‌دهد؟

شناسهٔ نصب، دامنه، پروفایل‌ها و نقش نود ذخیره می‌شوند. نسخهٔ فعلی عمداً تغییر بی‌صدای آن‌ها را رد می‌کند تا کانفیگ کاربران نشکند. فایل state را حذف نکن. برای تغییر اساسی از محیط جدید، بکاپ و برنامهٔ مهاجرت استفاده کن؛ [فصل ۱۱](11-backup-upgrade.md).
