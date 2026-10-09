# ۷. VLESS/REALITY/Vision و Shadowsocks TCP

[فهرست](README.md)

**اختیاری، برای نصب جدید Docker/VPS؛ نه مسیر معمول HTTPS در Railway.** در نصب قدیمی فقط متغیر را اضافه نکن یا فایل state را پاک نکن. فعلاً فعال‌سازی بی‌وقفهٔ این گزینه‌ها روی دیتابیس قبلی پیاده نشده است.

## دامنه و پورت

- `panel.example.com` برای پنل و اتصال‌های وب روی 443 باقی می‌ماند.
- `direct.example.com` رکورد مستقیم A/AAAA به VPS دارد. اگر Cloudflare استفاده می‌کنی، برای این رکورد DNS-only باشد؛ proxy معمولی HTTP جای TCP مستقیم نیست.
- REALITY روی **11443/TCP**، Shadowsocks روی **11444/TCP** است. در فایروال ارائه‌دهنده فقط پورت لازم را باز کن؛ mapping Docker را هم بررسی کن.
- `origin.example.com:443` باید سرویس TLS 1.3 سازگار تحت اختیار یا اجازهٔ تو باشد، با SNI معتبر. نشانی خود REALITY را target نکن؛ حلقهٔ forwarding ایجاد می‌کند. یک DNS alias دیگر به همان listener هم مجاز نیست.

## تنظیم قبل از اولین اجرا

در فایل `.env` خصوصی:

```dotenv
SABI_ADVANCED=reality,shadowsocks
SABI_DIRECT_DOMAIN=direct.example.com
SABI_REALITY_TARGET=origin.example.com:443
SABI_REALITY_SERVER_NAME=origin.example.com
```

فقط Shadowsocks می‌خواهی؟ `SABI_ADVANCED=shadowsocks` بگذار؛ target/SNI لازم نیست. فقط REALITY می‌خواهی؟ `SABI_ADVANCED=reality`. این نسخه پورت‌های خودکار مستقیم را ثابت انتخاب کرده تا آموزش و خروجی ساب همخوان باشند.

## اجرا

```sh
docker compose -f compose.yaml -f compose.vps.yaml -f compose.direct.yaml config --quiet
docker compose -f compose.yaml -f compose.vps.yaml -f compose.direct.yaml up -d --build
docker compose -f compose.yaml -f compose.vps.yaml -f compose.direct.yaml ps
```

فایل سوم دو mapping می‌سازد، اما listener فقط برای گزینهٔ فعال ساخته می‌شود. فایروال پورت غیرلازم را باز نکند. بعد از نصب موفق گروه `sabi-ray-all` شامل ورودی مستقیم هم هست. کاربر با قالب بساز و ساب را update کن.

## کلید REALITY

کلید X25519 و short ID به‌صورت محلی روی سرور تولید و در `sabi-reality.json` با مجوز 0600 ذخیره می‌شوند؛ نه داخل مخزن و نه در خروجی عمومی. در restart ثابت می‌مانند. کلید خصوصی را در کلاینت قرار نده؛ ساب اطلاعات لازم کلاینت را تولید می‌کند. فایل‌های Volume و بکاپ شامل اطلاعات حساس‌اند.

روی کاربر، flow مربوط به REALITY از تنظیمات inbound/هسته اعمال می‌شود و باید در خروجی تولیدشده Vision باشد. کلاینت جدید با پشتیبانی REALITY و Vision لازم است. در بعضی نسخه‌های Xray نام client publicKey به password تغییر کرده؛ لینک ساب را مطابق کلاینت سازگار import کن، نه اینکه privateKey را به‌جایش وارد کنی.

## Shadowsocks این نسخه دقیقاً چیست؟

این پیش‌تنظیم **Shadowsocks AEAD چندکاربره با TCP** است؛ SS2022 یا UDP را ادعا نمی‌کنیم. cipher و رمز هر کاربر از مدل پایهٔ پنل می‌آیند؛ پیش‌فرض chacha20-ietf-poly1305. `security=none` در لایهٔ stream یعنی TLS بیرونی ندارد؛ خود پروتکل رمزنگاری AEAD دارد و این عبارت به معنی plaintext نیست. برای نیاز SS2022/UDP ابتدا سازگاری حساب‌ها و کلاینت را جدا بررسی کن.

## راستی‌آزمایی و خطر target

REALITY ممکن است اتصال احرازنشده را به target هدایت کند؛ مقصد را با آگاهی و اجازه انتخاب کن و مصرف/سوءاستفاده را پایش کن. این روش سرویس را «غیرقابل تشخیص» یا «تضمیناً سریع» نمی‌کند.

خروجی مورد انتظار: در ساب کاربر، یک VLESS با security=reality و یک ss:// مطابق انتخاب‌ها دیده شود؛ با دستگاه خارج از سرور هر کدام جدا تست شود. اتصال داخل CI حتی با handshake واقعی، پینگ اینترنت تو یا سیاست شبکهٔ میزبان را تأیید نمی‌کند.

مراجع: https://xtls.github.io/en/config/transports/reality.html و https://xtls.github.io/en/config/inbounds/shadowsocks.html
