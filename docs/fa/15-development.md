# ۱۵. API، توسعه و مشارکت

[فهرست](README.md)

## ساختار پوشه‌ها

- `app/`: backend پایهٔ PasarGuard؛ تغییر نام importها برای برند لازم نیست.
- `dashboard/`: React/Vite؛ تغییرات ظاهری واقعی و ترجمه‌ها.
- `sabi_ray/`: راه‌اندازی، پروفایل‌ها، کلیدهای مستقیم، health، backup و doctor.
- `tests_sabi/`: unit و تست Docker/مرورگر/انتقال داده.
- `docs/fa/`: این مرکز آموزش.
- `compose*.yaml` و `railway.json`: استقرار.

## تست محلی

```sh
python3 -m unittest discover -s tests_sabi -v
```

فایل‌های پایه ممکن است syntax مربوط به Python 3.14 داشته باشند؛ اعتبارسنجی کامل backend با Python 3.14 یا image ثابت انجام شود. به خطای مفسر قدیمی برچسب bug برنامه نزن.

```sh
docker build -t sabi-ray:local .
```

این فرمان build را آزمایش می‌کند، نه اتصال سرویس. تست کامل CI در `.github/workflows/sabi-ci.yml` است؛ کلیدها و کاربران آزمایشی آن موقت‌اند. برای توسعه branch جدا بساز؛ Volume عملیاتی را برای تست mount نکن.

## API امن

به‌جای قراردادن رمز مالک در اسکریپت، از API key با مجوز حداقلی و انقضا در پنل استفاده کن. کلید را در credential manager یا محیط خصوصی زمان اجرا قرار بده. لینک endpoint و schema دقیق از نسخهٔ نصب‌شده بررسی شود؛ docs/OpenAPI ممکن است بسته به تنظیمات برنامه عمومی نباشد.

نمونهٔ read-only با ورودی پنهان، روی دستگاه مورد اعتماد خودت:

```python
import getpass, json, urllib.request
base = input('HTTPS panel URL: ').rstrip('/')
if not base.startswith('https://'):
    raise ValueError('Use HTTPS')
key = getpass.getpass('API key (hidden): ')
request = urllib.request.Request(
    base + '/api/users?limit=10',
    headers={'Accept': 'application/json', 'X-Api-Key': key},
)
with urllib.request.urlopen(request, timeout=20) as response:
    result = json.load(response)
print('Total visible users:', result.get('total'))
```

فقط URL پنل خودت را وارد کن؛ کلید را به دامنهٔ ناشناس نفرست. این نمونه دادهٔ کاربران یا توکن اشتراک را چاپ نمی‌کند. scope کلید/نقش تعیین می‌کند چه چیزی قابل مشاهده است.

## انتشار تغییر

- کلید، `.env`، SQLite، QR یا بکاپ وارد Git نکن.
- تست، شرح تغییر، احتمال قطعی و مسیر rollback را همراه PR بده.
- تعداد قابلیت‌ها را از روی تعداد دکمه یا fingerprint نشمار.
- وقتی فرمت subscription یا group/tag عوض می‌شود، کلاینت‌های موجود و دادهٔ قبلی را در تست پوشش بده.
- نسخهٔ dependency/image را بدون توضیح و تست عوض نکن.
- LICENSE و NOTICE و دسترسی به Corresponding Source حفظ شود.
