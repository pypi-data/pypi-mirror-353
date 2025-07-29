# MarketClock ⏰📊

MarketClock یک ماژول پایتون پیشرفته برای بررسی باز یا بسته بودن بازارهای مالی در زمان‌های مختلف و تحلیل حجم معاملات است.

## امکانات اصلی

- بررسی وضعیت باز یا بسته بودن بازارها (همراه با timezone و تعطیلات رسمی)
- نمایش مدت‌زمان باقی‌مانده تا بسته‌شدن هر بازار
- ذخیره خروجی به فرمت JSON یا CSV
- پشتیبانی از APIهای خارجی مانند AlphaVantage و Binance برای تحلیل حجم معاملات
- توابع کمکی برای نمایش، ذخیره و ترندگیری

## نصب

```bash
pip install marketclock
```

یا اگر لوکال توسعه می‌دهید:

```bash
git clone https://github.com/yourusername/marketclock.git
cd marketclock
pip install -e .
```

## استفاده

```python
from marketclock import MarketClock

mc = MarketClock(alpha_api_key="YOUR_API_KEY")
res = mc.get_open_markets_json()
print(res)
```

## لایسنس

این پروژه تحت مجوز MIT ارائه شده است. برای اطلاعات بیشتر فایل `LICENSE` را ببینید.
