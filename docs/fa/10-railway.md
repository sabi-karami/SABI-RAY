# ۱۰. Railway: نصب مشروط، نه دورزدن محدودیت

[فهرست](README.md)

**قبل از Deploy:** سیاست Railway اجرای proxies / anonymization services را ممنوع کرده است. کاربرد دقیق را با پشتیبانی روشن و اجازهٔ لازم را دریافت کن. این مخزن اجازهٔ ارائه‌دهنده را صادر یا تأیید نمی‌کند. از نسخهٔ 0.2.0-alpha.2 متغیر `RAILWAY_APPROVAL_CONFIRMED` لازم نیست و نادیده گرفته می‌شود؛ دربارهٔ مقررات فقط هشدار غیرمسدودکننده ثبت می‌شود. پنل control-only هم خودکار معاف فرض نمی‌شود.

سیاست رسمی: https://railway.com/legal/acceptable-use

## اگر کاربردت تأیید شده است

۱. از Railway یک پروژهٔ جدید، Deploy from GitHub repo و `sabi-karami/SABI-RAY` را انتخاب کن. این کار ممکن است هزینه ایجاد کند؛ محدودیت هزینه تنظیم کن.
۲. Dockerfile ریشه مبنای build است. branch/tag انتخابی را با release و گزارش تست تطبیق بده.
۳. یک Volume به مسیر `/var/lib/pasarguard` وصل کن؛ Replica برابر ۱.
۴. در Variables، `DEPLOY_MODE=railway` را قرار بده. متغیر `RAILWAY_APPROVAL_CONFIRMED` لازم نیست؛ وجود مقدار قدیمی false هم دیگر این توقف را ایجاد نمی‌کند.
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

## رفع توقف نسخه‌های قبلی

اگر لاگ با `Startup stopped: Railway prohibits proxy/anonymization services` تمام می‌شود، نسخهٔ قدیمی در حال اجراست. تغییر کد در main یا release `v0.2.0-alpha.2` را **Build و Deploy** کن؛ restart/redeploy همان image قدیمی کافی نیست. متغیر تأییدیه را true جعل نکن.

- GitHub source و branch سرویس را بررسی کن؛ تغییر باید از `sabi-karami/SABI-RAY` و commit اصلاح‌شده دریافت شود.
- Volume، رمز مالک، domain و profileها را برای رفع این توقف عوض یا پاک نکن.
- بعد از build جدید انتظار `WARNING: Railway deployment detected` داری، نه همان `Startup stopped`. هشدار به‌تنهایی خطا نیست.
- باقی پیش‌نیازها حفظ شده‌اند: رمز اولیه فقط برای نصب جدید، domain معتبر و Volume؛ SABI_ADVANCED روی Railway خالی باشد.
- `/healthz` باید پس از راه‌اندازی واقعی ready شود؛ این راهنما ادعا نمی‌کند deployment خارجی تو از این چت تست شده است.
