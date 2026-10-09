# ۱۰. Railway: نصب مشروط، نه دورزدن محدودیت

[فهرست](README.md)

**قبل از Deploy:** سیاست Railway اجرای proxies / anonymization services را ممنوع کرده است. کاربرد دقیق را با پشتیبانی روشن و اجازهٔ لازم را دریافت کن. این مخزن و `RAILWAY_APPROVAL_CONFIRMED=true` خودشان اجازه صادر نمی‌کنند. پنل control-only هم خودکار معاف فرض نمی‌شود.

سیاست رسمی: https://railway.com/legal/acceptable-use

## اگر کاربردت تأیید شده است

۱. از Railway یک پروژهٔ جدید، Deploy from GitHub repo و `sabi-karami/SABI-RAY` را انتخاب کن. این کار ممکن است هزینه ایجاد کند؛ محدودیت هزینه تنظیم کن.
۲. Dockerfile ریشه مبنای build است. branch/tag انتخابی را با release و گزارش تست تطبیق بده.
۳. یک Volume به مسیر `/var/lib/pasarguard` وصل کن؛ Replica برابر ۱.
۴. در Variables، `DEPLOY_MODE=railway` و پس از اجازهٔ واقعی `RAILWAY_APPROVAL_CONFIRMED=true` را قرار بده.
۵. SABI_ADMIN_USER و SABI_INITIAL_PASSWORD قوی را در Variables وارد کن. در GitHub ذخیره نکن.
۶. `SABI_PROFILES=vless-ws,trojan-ws,vmess-ws`، `SABI_ADVANCED` خالی، `PORT=8080`.
۷. Networking → Generate Domain با target port 8080. runtime از RAILWAY_PUBLIC_DOMAIN استفاده می‌کند؛ اگر دامنه در شروع نخست موجود نبود، بعد از ساخت دامنه Redeploy کن.
۸. برای دامنهٔ اختصاصی، DNS و صحت گواهی Railway را کامل و PUBLIC_DOMAIN را پیش از setup نهایی مشخص کن.
۹. `/healthz` و سپس `/dashboard/` را بررسی کن. اگر سلامت برقرار نشد [فصل ۱۲](12-troubleshooting.md)، نه دستکاری کورکورانهٔ state.
۱۰. پس از setup موفق، رمز اولیه را از Variables حذف و Redeploy کن؛ Volume را نگه دار.

## مرزهای فنی

- دامنهٔ HTTPS و TLS edge با پورت TCP proxy یکسان نیستند.
- قابلیت UDP شبکهٔ خصوصی Railway اثبات UDP عمومی برای کلاینت VPN نیست.
- REALITY/Hysteria2/WireGuard را پشت HTTPS معمولی فعال فرض نکن. راه‌اندازی خودکار direct در این نسخه روی Railway رد می‌شود.
- هزینهٔ CPU/RAM/storage/egress را در نظر بگیر؛ «سورس رایگان» یعنی «میزبانی بدون هزینه» نیست.
- Healthcheck راه‌اندازی را می‌سنجد؛ اتصال واقعی یک کلاینت از بیرون باید جدا تست شود.

**این پروژه از طرف این چت روی Railway مستقر نشده و اجازهٔ میزبان هم دریافت نشده است.**
