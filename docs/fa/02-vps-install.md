# ۲. نصب کامل روی VPS

[فهرست](README.md) · [مرحلهٔ بعد](03-configuration.md)

## پیش‌نیاز

- سرور لینوکسی با SSH و دسترسی مدیریت؛ نصب روی VPS مجاز نزد ارائه‌دهنده.
- Docker Engine و افزونهٔ Docker Compose v2 از مستندات رسمی: https://docs.docker.com/engine/install/
- Git و Python 3 برای ابزار نصب تعاملی. دستورها روی یک میزبان لینوکسی اجرا می‌شوند.
- دامنهٔ `panel.example.com` با رکورد A به IPv4 سرور. فقط وقتی IPv6 واقعاً برقرار است AAAA بساز.
- پورت 80/TCP و 443/TCP آزاد؛ هیچ nginx/apache دیگری روی همان پورت‌ها نباشد.

قبل از تغییر فایروال، راه ورود SSH را در فایروال سیستم و فایروال ارائه‌دهنده حفظ کن. Docker ممکن است قواعد بعضی ابزارها مثل UFW را دور بزند؛ فایروال ارائه‌دهنده و DOCKER-USER را طبق مستندات Docker بررسی کن. پورت 8080 در بستهٔ پایه فقط روی loopback منتشر می‌شود.

## ۱) بررسی ابزارها

```sh
docker version
docker compose version
git --version
python3 --version
```

اگر Docker نیاز به sudo دارد همان سیاست را برای تمام دستورها رعایت کن؛ عضویت در گروه docker عملاً دسترسی سطح root می‌دهد.

## ۲) دریافت نسخه

```sh
git clone https://github.com/sabi-karami/SABI-RAY.git
cd SABI-RAY
git checkout v0.2.0-alpha.1
```

در زمان توسعه اگر tag هنوز منتشر نشده، از آخرین نسخهٔ منتشرشده در Releases استفاده کن؛ نصب از main ممکن است بین تغییرات آزمایشی قرار بگیرد.

## ۳) ساخت فایل خصوصی تنظیمات

```sh
python3 scripts/init-env.py
```

دامنه را بدون `https://` وارد کن. نام مالک پیش‌فرض `owner` است. رمز در ترمینال نمایش داده نمی‌شود؛ حداقل ۱۶ کاراکتر شامل حروف بزرگ/کوچک، عدد و نماد انتخاب و در مدیر رمز ذخیره کن. ابزار فایل موجود را بازنویسی نمی‌کند و `.env` را با دسترسی 0600 می‌سازد. اگر از ابزار استفاده نمی‌کنی:

```sh
umask 077
cp .env.sabi.example .env
chmod 600 .env
nano .env
```

هیچ رمز را در GitHub، چت یا اسکرین‌شات ننویس. برای نسخهٔ ساده SABI_ADVANCED خالی بماند. برای پروتکل مستقیم **پیش از اولین اجرا** [فصل ۷](07-direct-protocols.md) را انجام بده.

## ۴) ساخت و اجرا

```sh
docker compose -f compose.yaml -f compose.vps.yaml config --quiet
docker compose -f compose.yaml -f compose.vps.yaml up -d --build
docker compose -f compose.yaml -f compose.vps.yaml ps
```

خروجی مورد انتظار: panel به حالت healthy برسد؛ سپس edge بالا بیاید. ساخت اول ممکن است زمان‌بر باشد. Caddy با دامنهٔ واقعی و بازبودن پورت‌ها گواهی صادر می‌کند. اگر دامنه را هنوز آماده نکرده‌ای، تغییر تصادفی تنظیمات را جایگزین عیب‌یابی نکن.

## ۵) بررسی

```sh
curl -fsS https://panel.example.com/healthz
docker compose -f compose.yaml -f compose.vps.yaml exec -T panel python -m sabi_ray.doctor
```

پاسخ سلامت `{"status":"ready"}` است. در مرورگر `https://panel.example.com/dashboard/` را باز کن؛ با owner و رمز انتخابی خودت وارد شو. سپس کاربر آزمایشی با قالب بساز و از دستگاه دیگر اشتراک را تست کن. صرف بالا آمدن صفحه، اثبات اتصال پروکسی نیست.

## ۶) حذف رمز اولیه از محیط

پس از موفقیت کامل راه‌اندازی و ذخیرهٔ رمز در جای امن، خط `SABI_INITIAL_PASSWORD` را از `.env` حذف کن و کانتینر را دوباره ایجاد کن:

```sh
docker compose -f compose.yaml -f compose.vps.yaml up -d --force-recreate panel
```

رمز در دیتابیس می‌ماند و به مقدار پیش‌فرض ریست نمی‌شود. قبل از تکمیل setup رمز اولیه را حذف نکن. در صورت فراموشی [بازیابی مالک](13-security.md) را انجام بده.

## توقف بدون حذف اطلاعات

```sh
docker compose -f compose.yaml -f compose.vps.yaml stop
```

**`down -v` اجرا نکن؛ Volume و داده‌ها را حذف می‌کند.**
