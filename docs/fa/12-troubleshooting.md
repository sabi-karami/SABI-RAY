# ۱۲. عیب‌یابی مرحله‌به‌مرحله

[فهرست](README.md)

## شروع بی‌خطر

```sh
docker compose -f compose.yaml -f compose.vps.yaml ps
docker compose -f compose.yaml -f compose.vps.yaml logs --tail=80 panel
docker compose -f compose.yaml -f compose.vps.yaml logs --tail=80 edge
docker compose -f compose.yaml -f compose.vps.yaml exec -T panel python -m sabi_ray.doctor
```

در نصب direct فایل سوم را اضافه کن. خروجی doctor عمداً domain، UUID، token و key چاپ نمی‌کند. بااین‌حال گزارش‌ها را قبل از ارسال بررسی کن. لاگ خام پایه ممکن است اطلاعات کاربری داشته باشد؛ `.env` یا `docker inspect` را نفرست.

| علامت | بررسی | اقدام |
|---|---|---|
| build شکست می‌خورد | اولین خط خطای واقعی، RAM/disk/network | فضای کافی، دسترسی registry؛ نسخهٔ قفل‌شده را بی‌دلیل تغییر نده |
| restart loop پیش از پنل | PUBLIC_DOMAIN، رمز اولیه، مجوز Railway | متغیرها را مطابق راهنما اصلاح کن؛ حذف Volume نکن |
| Deployment settings changed | state و env متفاوت شده‌اند | env قبلی را برگردان؛ مهاجرت برنامه‌ریزی‌شده |
| رمز قوی رد می‌شود | طول، انواع کاراکتر، quote/dollar | از ابزار init-env و مدیر رمز استفاده کن |
| 502/503 | panel healthy؟ edge؟ listener؟ | logs و doctor؛ بازبودن nginx به تنهایی کافی نیست |
| HTTPS گواهی نمی‌گیرد | A/AAAA، 80/443، سرویس رقیب، CDN | DNS/پورت را درست کن؛ TLS verification را خاموش نکن |
| ورود 429 | تلاش‌های زیاد / rate limit | مکث، بررسی ترافیک؛ پشت edge ممکن است IPها مشترک شمرده شوند |
| ورود صحیح نیست | owner نام درست، setup کامل | از reset خودکار محیطی انتظار نداشته باش؛ فصل امنیت |
| ساب خالی | گروه، inbound tag، host فعال | کاربر با قالب صحیح بساز؛ نود سالم باشد |
| WS کار می‌کند XHTTP نه | نسخهٔ کلاینت، mode، proxy buffering | کلاینت سازگار و packet-up؛ مسیر کامل |
| REALITY وصل نمی‌شود | direct DNS، 11443/TCP، target TLS/SNI/shortId | تست از بیرون؛ هدف به listener خودت loop نزند |
| Shadowsocks وصل نمی‌شود | 11444/TCP، cipher، رمز تولیدی | ساب را update کن؛ انتظار UDP از preset TCP نداشته باش |
| نود بعد از حدود یک سال بالا نمی‌آید | گواهی داخلی تولید اولیه ۳۶۵روزه | برنامهٔ تمدید گواهی و ثبت CA جدید لازم است؛ خودکار نیست |
| مصرف دیر دیده می‌شود | فاصلهٔ جمع‌آوری آمار | زمان بده، core/user association را بررسی کن |
| بعد از restart اطلاعات نیست | Volume واقعاً متصل است؟ | اتصال Volume قبلی؛ قبل از نوشتن جدید توقف و بازیابی |

## تشخیص لایهٔ مشکل

۱. DNS دامنه → ۲. TCP پورت → ۳. TLS/SNI → ۴. مسیر transport → ۵. UUID/رمز کاربر → ۶. DNS/route مقصد → ۷. سهمیه/انقضا.

همه را همزمان عوض نکن؛ هر بار یک تغییر، تست و ثبت. اگر خطای کانفیگ شامل دادهٔ محرمانه است، قبل از issue بخش محرمانه را حذف کن.

## گزارش قابل بررسی

نسخهٔ release، سیستم عامل سرور و کلاینت، نام پروتکل/transport، زمان خطا، operator اینترنت (در صورت تمایل)، نتیجهٔ سلامت و بخش کوتاه لاگ سانسورشده. رمز، token، کلید خصوصی، QR یا لینک کامل ساب لازم نیست.

## اصلاحات مهم نسخهٔ 0.2

- security در Host مربوط به REALITY از inbound ارث می‌برد؛ override رشتهٔ reality در API پایه معتبر نبود.
- اعلام سلامت نصب اولیه منتظر ثبت کامل نود connected می‌ماند تا ساخت سریع کاربر با آغاز نود رقابت نکند.
- رمز اولیه قبل از ساخت دیتابیس/کاربر با قواعد واقعی پایه بررسی می‌شود.

جزئیات و مرز تست‌ها در [گزارش انتشار](../BUILD-REPORT.md) ثبت شده‌اند.

## خطای Startup stopped دربارهٔ مقررات Railway

در نسخه‌های پیش از 0.2.0-alpha.2، شرط داخلی برنامه بدون متغیر تأییدیه exit می‌کرد. این رفتار به هشدار غیرمسدودکننده تبدیل شده است؛ به معنی تأیید مقررات از طرف Railway نیست. سورس نسخهٔ اصلاح‌شده را rebuild/deploy کن، نه اینکه فقط image قدیمی را restart کنی. `RAILWAY_APPROVAL_CONFIRMED=true` دیگر لازم نیست و داده/Volume را نباید پاک کرد. [راهنمای دقیق](10-railway.md).
