from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Iterable, Callable
import pandas as pd
import pytz
import json
import csv
import requests
import logging


class MarketClock:
    """
    همه‌کاره برای دریافت وضعیت بازارها، زمان‌بندی‌ها و داده‌های حجم بازارها
    • توسعه‌پذیر + منعطف + قابل استفاده در backend و frontend و تحلیل داده
    """
    def _init_logger(self):
        self.logger = logging.getLogger("MarketClock")
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __init__(
        self,
        markets: Optional[Dict[str, dict]] = None,
        alpha_api_key: Optional[str] = None,
        timezone: str = "UTC",
        log_level: int = logging.WARNING,
    ):
        self.default_markets = self._get_default_markets()
        self._init_logger()
        self.markets = markets if markets is not None else self.default_markets
        self.alpha_api_key = alpha_api_key or "GAF8C8R1U6W4ROW5"
        self.timezone = timezone
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.cache = {}  # برای داده‌های حجیم API

    @staticmethod
    def _get_default_markets() -> Dict[str, dict]:
        """تعریف بازارهای اصلی دنیا
        اگر می‌خواهی بازار اختصاصی خود را اضافه کنی، کافی در زمان ساخت کلاس دیتا بدهی."""

        return {
            "NYSE": {
                "timezone": "America/New_York",
                "sessions": [((9, 30), (16, 0))],
                "country_code": "US",
                "holidays": []
            },
            "Nasdaq": {
                "timezone": "America/New_York",
                "sessions": [((9, 30), (16, 0))],
                "country_code": "US",
                "holidays": []
            },
            "London (LSE)": {
                "timezone": "Europe/London",
                "sessions": [((8, 0), (16, 30))],
                "country_code": "GB",
                "holidays": []
            },
            "Frankfurt (Xetra)": {
                "timezone": "Europe/Berlin",
                "sessions": [((9, 0), (17, 30))],
                "country_code": "DE",
                "holidays": []
            },
            "Tokyo (TSE)": {
                "timezone": "Asia/Tokyo",
                "sessions": [((9, 0), (11, 30)), ((12, 30), (15, 0))],
                "country_code": "JP",
                "holidays": []
            },
            "Shanghai (SSE)": {
                "timezone": "Asia/Shanghai",
                "sessions": [((9, 30), (11, 30)), ((13, 0), (15, 0))],
                "country_code": "CN",
                "holidays": []
            },
            "Hong Kong (HKEX)": {
                "timezone": "Asia/Hong_Kong",
                "sessions": [((9, 30), (12, 0)), ((13, 0), (16, 0))],
                "country_code": "HK",
                "holidays": []
            },
            "Sydney (ASX)": {
                "timezone": "Australia/Sydney",
                "sessions": [((10, 0), (16, 0))],
                "country_code": "AU",
                "holidays": []
            },
            "Toronto (TSX)": {
                "timezone": "America/Toronto",
                "sessions": [((9, 30), (16, 0))],
                "country_code": "CA",
                "holidays": []
            },
            "Mumbai (NSE)": {
                "timezone": "Asia/Kolkata",
                "sessions": [((9, 15), (15, 30))],
                "country_code": "IN",
                "holidays": []
            },
            "Moscow (MOEX)": {
                "timezone": "Europe/Moscow",
                "sessions": [((9, 30), (19, 0))],
                "country_code": "RU",
                "holidays": []
            },
            "Johannesburg (JSE)": {
                "timezone": "Africa/Johannesburg",
                "sessions": [((9, 0), (17, 0))],
                "country_code": "ZA",
                "holidays": []
            },
            "Sao Paulo (B3)": {
                "timezone": "America/Sao_Paulo",
                "sessions": [((10, 0), (17, 30))],
                "country_code": "BR",
                "holidays": []
            },
            "Dubai (DFM)": {
                "timezone": "Asia/Dubai",
                "sessions": [((10, 0), (14, 0))],
                "country_code": "AE",
                "holidays": []
            },
            "Riyadh (Tadawul)": {
                "timezone": "Asia/Riyadh",
                "sessions": [((10, 0), (15, 0))],
                "country_code": "SA",
                "holidays": []
            }
        }

    # ========== مدیریت بازارها و تعطیلات ==========
    def add_market(self, name: str, info: dict):
        """افزودن بازار جدید"""
        self.markets[name] = info

    def add_session_to_market(self, market: str, session: Iterable):
        """افزودن سشین به بازار"""
        self.markets[market]["sessions"].append(session)

    def add_holidays_to_market(self, market: str, holidays: List[str]):
        """افزودن لیست تعطیلات به بازار"""
        self.markets[market].setdefault("holidays", []).extend(holidays)
   
    def add_holiday(self, market_name, date):
        """
        یک روز به تعطیلات این بازار اضافه می‌کند. date به فرمت 'YYYY-MM-DD'
        """
        if market_name in self.markets:
            if date not in self.markets[market_name]['holidays']:
                self.markets[market_name]['holidays'].append(date)

    def set_holidays(self, market_name, holiday_list):
        """
        لیست تعطیلی جدید (کلاً جایگزین می‌شود) به بازار می‌دهد.
        """
        if market_name in self.markets:
            self.markets[market_name]['holidays'] = holiday_list.copy()

    def set_market_timezone(self, market: str, timezone: str):
        """تغییر تایم‌زون بازار"""
        self.markets[market]['timezone'] = timezone

    # ========== توابع تبدیل و مدیریت زمان ==========
    def parse_time(
        self,
        input_time: Optional[Any] = None,
        timezone: Optional[str] = None,
    ) -> datetime:
        """
        ورودی را به datetime تایم‌زون‌شده تبدیل می‌کند.
        input_time: None, str, datetime, timestamp
        timezone: string
        """
        tzname = timezone or self.timezone
        tz = pytz.timezone(tzname)
        if input_time is None:
            base_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
        elif isinstance(input_time, (int, float)):
            base_time = datetime.utcfromtimestamp(input_time).replace(tzinfo=pytz.UTC)
        elif isinstance(input_time, str):
            try:
                base_time = datetime.fromisoformat(input_time)
            except ValueError:
                raise ValueError("Invalid datetime string.")
        elif isinstance(input_time, datetime):
            base_time = input_time
        else:
            raise TypeError("Unsupported input_time type")
        # Always output as tz-aware datetime in desired tz
        if base_time.tzinfo is None:
            base_time = pytz.UTC.localize(base_time)
        return base_time.astimezone(tz)

    # ========== پرس و جوی وضعیت بازارها ==========
    def get_open_markets(self, input_time=None, timezone="UTC"):
        check_time_utc = self.parse_time(input_time, timezone)
        result = []

        for name, info in self.markets.items():
            tz = pytz.timezone(info["timezone"])
            local_time = check_time_utc.astimezone(tz)

            date_str = local_time.strftime('%Y-%m-%d')
            if date_str in info.get("holidays", []):
                continue

            is_open = False
            remaining_time = "Closed"
            for (start_h, start_m), (end_h, end_m) in info["sessions"]:
                start = local_time.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                end = local_time.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                if start <= local_time <= end:
                    is_open = True
                    remaining_time = str(end - local_time).split('.')[0]
                    break

            result.append({
                "market": name,
                "local_time": local_time.strftime('%H:%M:%S'),
                "remaining_time": remaining_time,
                "timezone": info["timezone"],
                "is_open": is_open
            })

        return result

    def filter_markets(
        self, country_code: Optional[str] = None, is_open: Optional[bool] = None
    ) -> List[str]:
        """لیست بازارها بر اساس کد کشور یا باز/بسته بودن"""
        data = self.get_open_markets()
        result = []
        for m in data:
            if (country_code is None or m["country_code"] == country_code) and \
               (is_open is None or m["is_open"] == is_open):
                result.append(m["market"])
        return result

    # ========== خروجی داده ==========
    def export_data(self, data: List[dict], fmt: str = "dict", filename: Optional[str] = None):
        """
        خروجی به فرمت دلخواه (dict, json, csv)
        """
        if fmt == "dict":
            return data
        elif fmt == "json":
            jstring = json.dumps(data, ensure_ascii=False, indent=2)
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(jstring)
            return jstring
        elif fmt == "csv":
            if not filename:
                raise ValueError("For csv export, specify filename.")
            with open(filename, "w", encoding="utf-8", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        else:
            raise ValueError("Format not supported")

    # ========== داده حجم بازار و تعطیلات (API) ==========
    def fetch_binance_volume_data(self, symbol="BTCUSDT", interval="1m", limit=100):
        url = f"https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        try:
            res = requests.get(url, params=params)
            if res.status_code != 200:
                self.logger.error(f"Binance API Error: {res.text}")
                return []
            data = res.json()
            return [{"time": datetime.utcfromtimestamp(d[0] / 1000), "volume": float(d[5])} for d in data]
        except Exception as e:
            self.logger.error(f"❌ خطا در دریافت داده از Binance: {e}")
            return []


    def get_avg_volume(self, symbol="BTCUSDT", interval="1m", limit=30):
        volume_data = self.fetch_binance_volume_data(symbol, interval, limit)
        if not volume_data:
            return None
        avg_volume = sum(d["volume"] for d in volume_data) / len(volume_data)
        return round(avg_volume, 2)

    def fetch_public_holidays(self, year: int, country_code: str) -> List[str]:
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
        response = requests.get(url)
        if response.status_code == 200:
            holidays = response.json()
            return [holiday['date'] for holiday in holidays]
        else:
            self.logger.error(f"Error fetching holidays for {country_code}, {year}")
            return []

    # ========== ابزارهای توسعه و log ==========
    def set_log_level(self, level: int):
        """تعیین سطح لاگ کد"""
        self.logger.setLevel(level)

    def __repr__(self):
        return f"<MarketClock: {len(self.markets)} markets, default tz={self.timezone}>"

    # ========== نمونه‌های ایستا (static) ==========
    @staticmethod
    def check_market_open_static(info: dict, at_time) -> bool:
        """بررسی باز بودن بازار در زمان مشخص (تایم‌استمپ، رشته، datetime)"""
        
        # تبدیل ورودی به datetime timezone-aware
        if isinstance(at_time, (int, float)):
            at_time = datetime.utcfromtimestamp(at_time).replace(tzinfo=pytz.utc)
        elif isinstance(at_time, str):
            try:
                at_time = datetime.fromisoformat(at_time)
            except ValueError:
                raise ValueError("❌ رشته زمان نامعتبر است.")
        elif isinstance(at_time, datetime):
            if at_time.tzinfo is None:
                at_time = at_time.replace(tzinfo=pytz.utc)
        else:
            raise TypeError("❌ نوع ورودی at_time نامعتبر است.")

        # تبدیل زمان به زمان محلی بازار
        local_time = at_time.astimezone(pytz.timezone(info["timezone"]))
        date_str = local_time.strftime('%Y-%m-%d')

        if date_str in info.get("holidays", []):
            return False

        for (start_h, start_m), (end_h, end_m) in info["sessions"]:
            start = local_time.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
            end = local_time.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
            if start <= local_time <= end:
                return True

        return False
    def detect_user_timezone(self) -> str:
        """
        منطقه زمانی کاربر را بر اساس IP (آنلاین) تشخیص می‌دهد و به عنوان zone پیش‌فرض کلاس ست می‌کند.
        """
        try:
            r = requests.get("https://ipapi.co/timezone/")
            if r.status_code == 200:
                tz = r.text.strip()
                self.timezone = tz
                return tz
            else:
                self.logger.warning(f"Could not auto-detect timezone (status {r.status_code})")
                return "UTC"
        except Exception as e:
            self.logger.error(f"Error auto-detecting timezone: {e}")
            return "UTC"

    def get_open_markets_df(self, input_time=None, timezone="UTC", filter_func=None):
        """
        خروجی لیست همه بازارها (یا طبق فیلتر)، به صورت یک DataFrame پاندا.
        """
        data = self.get_open_markets(input_time=input_time, timezone=timezone, filter_func=filter_func)
        return pd.DataFrame(data)

    def get_market_sessions(self, market_name: str) -> List[Dict[str, Any]]:
        """
        دریافت سشن‌های بازار به صورت لیست دیکشنری.
        """
        if market_name not in self.markets:
            raise ValueError(f"Market {market_name} not found.")
        market_info = self.markets[market_name]
        sessions = []
        for (start_h, start_m), (end_h, end_m) in market_info["sessions"]:
            sessions.append({
                "start": f"{start_h:02}:{start_m:02}",
                "end": f"{end_h:02}:{end_m:02}",
                "timezone": market_info["timezone"]
            })
        return sessions

    def get_market_info(self, market_name: str) -> Dict[str, Any]:
        """
        دریافت اطلاعات کلی بازار به صورت دیکشنری.
        """
        if market_name not in self.markets:
            raise ValueError(f"Market {market_name} not found.")
        return self.markets[market_name]
    def get_market_holidays(self, market_name: str) -> List[str]:
        """
        دریافت روزهای تعطیل بازار به صورت لیست.
        """
        if market_name not in self.markets:
            raise ValueError(f"Market {market_name} not found.")
        return self.markets[market_name].get("holidays", [])
    def get_market_timezone(self, market_name: str) -> str:
        """
        دریافت منطقه زمانی بازار به صورت رشته.
        """
        if market_name not in self.markets:
            raise ValueError(f"Market {market_name} not found.")
        return self.markets[market_name].get("timezone", "UTC")
    def get_market_country_code(self, market_name: str) -> Optional[str]:
        """
        دریافت کد کشور بازار به صورت رشته.
        """
        if market_name not in self.markets:
            raise ValueError(f"Market {market_name} not found.")
        return self.markets[market_name].get("country_code", None)
    def get_market_sessions_df(self, market_name: str) -> pd.DataFrame:
        """
        دریافت سشن‌های بازار به صورت DataFrame پاندا.
        """
        sessions = self.get_market_sessions(market_name)
        return pd.DataFrame(sessions)
    def get_market_holidays_df(self, market_name: str) -> pd.DataFrame:
        """
        دریافت روزهای تعطیل بازار به صورت DataFrame پاندا.
        """
        holidays = self.get_market_holidays(market_name)
        return pd.DataFrame(holidays, columns=["date"])
    def get_market_info_df(self, market_name: str) -> pd.DataFrame:
        """
        دریافت اطلاعات کلی بازار به صورت DataFrame پاندا.
        """
        info = self.get_market_info(market_name)
        return pd.DataFrame([info])
    def get_market_country_code_df(self, market_name: str) -> pd.DataFrame:
        """
        دریافت کد کشور بازار به صورت DataFrame پاندا.
        """
        country_code = self.get_market_country_code(market_name)
        return pd.DataFrame([{"country_code": country_code}])   
    def get_market_timezone_df(self, market_name: str) -> pd.DataFrame:
        """
        دریافت منطقه زمانی بازار به صورت DataFrame پاندا.
        """
        timezone = self.get_market_timezone(market_name)
        return pd.DataFrame([{"timezone": timezone}])   
    def get_market_sessions_json(self, market_name: str) -> str:
        """
        دریافت سشن‌های بازار به صورت JSON.
        """
        sessions = self.get_market_sessions(market_name)
        return json.dumps(sessions, ensure_ascii=False)
    def get_market_holidays_json(self, market_name: str) -> str:
        """
        دریافت روزهای تعطیل بازار به صورت JSON.
        """
        holidays = self.get_market_holidays(market_name)
        return json.dumps(holidays, ensure_ascii=False)
    def get_market_info_json(self, market_name: str) -> str:
        """
        دریافت اطلاعات کلی بازار به صورت JSON.
        """
        info = self.get_market_info(market_name)
        return json.dumps(info, ensure_ascii=False) 
    def get_market_country_code_json(self, market_name: str) -> str:
        """
        دریافت کد کشور بازار به صورت JSON.
        """
        country_code = self.get_market_country_code(market_name)
        return json.dumps({"country_code": country_code}, ensure_ascii=False)
    def get_market_timezone_json(self, market_name: str) -> str:
        """
        دریافت منطقه زمانی بازار به صورت JSON.
        """
        timezone = self.get_market_timezone(market_name)
        return json.dumps({"timezone": timezone}, ensure_ascii=False)   
    def get_market_sessions_csv(self, market_name: str, filename: str):
        """ دریافت سشن‌های بازار به صورت CSV.
        """
        sessions = self.get_market_sessions(market_name)
        df = pd.DataFrame(sessions)
        df.to_csv(filename, index=False)    
    def get_market_holidays_csv(self, market_name: str, filename: str):
        """ دریافت روزهای تعطیل بازار به صورت CSV.
        """
        holidays = self.get_market_holidays(market_name)
        df = pd.DataFrame(holidays, columns=["date"])
        df.to_csv(filename, index=False)
    def get_market_info_csv(self, market_name: str, filename: str):
        """ دریافت اطلاعات کلی بازار به صورت CSV.
        """
        info = self.get_market_info(market_name)
        df = pd.DataFrame([info])
        df.to_csv(filename, index=False)    
    def get_market_country_code_csv(self, market_name: str, filename: str):
        """ دریافت کد کشور بازار به صورت CSV.
        """
        country_code = self.get_market_country_code(market_name)
        df = pd.DataFrame([{"country_code": country_code}])
        df.to_csv(filename, index=False)    
    def get_market_timezone_csv(self, market_name: str, filename: str):
        """ دریافت منطقه زمانی بازار به صورت CSV.
        """ 
        timezone = self.get_market_timezone(market_name)
        df = pd.DataFrame([{"timezone": timezone}])
        df.to_csv(filename, index=False)
    def get_open_markets_csv(self, input_time=None, timezone="UTC", filter_func=None, filename: str = "open_markets.csv"):
        """ دریافت بازارهای باز به صورت CSV.
        """
        open_markets = self.get_open_markets(input_time, timezone, filter_func)
        df = pd.DataFrame(open_markets)
        df.to_csv(filename, index=False)
    def get_open_markets_json(self, input_time=None, timezone="UTC", filter_func=None) -> str:
        """ دریافت بازارهای باز به صورت JSON.
        """ 
        open_markets = self.get_open_markets(input_time, timezone, filter_func)
        return json.dumps(open_markets, ensure_ascii=False, indent=2)
    def get_open_markets_dict(self, input_time=None, timezone="UTC", filter_func=None) -> List[Dict[str, Any]]:
        """ دریافت بازارهای باز به صورت دیکشنری.
        """
        open_markets = self.get_open_markets(input_time, timezone, filter_func)
        return open_markets
    def get_avg_volume_df(self, symbol="BTCUSDT", interval="1m", limit=30) -> pd.DataFrame:
        """ دریافت میانگین حجم بازار به صورت DataFrame.
        """
        avg_volume = self.get_avg_volume(symbol, interval, limit)
        return pd.DataFrame([{"symbol": symbol, "avg_volume": avg_volume}])
    def get_avg_volume_json(self, symbol="BTCUSDT", interval="1m", limit=30) -> str:
        """ دریافت میانگین حجم بازار به صورت JSON.
        """
        avg_volume = self.get_avg_volume(symbol, interval, limit)
        return json.dumps({"symbol": symbol, "avg_volume": avg_volume}, ensure_ascii=False)
    def get_avg_volume_csv(self, symbol="BTCUSDT", interval="1m", limit=30, filename: str = "avg_volume.csv"):
        """ دریافت میانگین حجم بازار به صورت CSV.
        """
        avg_volume = self.get_avg_volume(symbol, interval, limit)
        df = pd.DataFrame([{"symbol": symbol, "avg_volume": avg_volume}])
        df.to_csv(filename, index=False)
    def get_volume_trend_df(self, symbol="BTCUSDT", source="binance", start_time=None, end_time=None, interval="5min") -> pd.DataFrame:
        """ دریافت روند حجم بازار به صورت DataFrame.
        """
        volume_data = self.get_volume_trend(symbol, source, start_time, end_time, interval)
        return pd.DataFrame(volume_data)
    def get_volume_trend_json(self, symbol="BTCUSDT", source="binance", start_time=None, end_time=None, interval="5min") -> str:
        """ دریافت روند حجم بازار به صورت JSON.
        """ 
        volume_data = self.get_volume_trend(symbol, source, start_time, end_time, interval)
        return json.dumps(volume_data, ensure_ascii=False, indent=2)
    def get_volume_trend_csv(self, symbol="BTCUSDT", source="binance", start_time=None, end_time=None, interval="5min", filename: str = "volume_trend.csv"):
        """ دریافت روند حجم بازار به صورت CSV.
        """
        volume_data = self.get_volume_trend(symbol, source, start_time, end_time, interval)
        df = pd.DataFrame(volume_data)
        df.to_csv(filename, index=False)
    def get_volume_trend(self, symbol="BTCUSDT", source="binance", start_time=None, end_time=None, interval="5min") -> List[Dict[str, Any]]:        
        """
        دریافت روند حجم بازار از منبع مشخص (binance یا alphavantage).
        """
        if source == "binance":
            return self.fetch_binance_volume_data(symbol, interval)
        elif source == "alphavantage":
            # فرض بر این است که داده‌های Alpha Vantage در فرمت مشابهی هستند
            return self.fetch_alphavantage_volume_data(symbol, interval)
        else:
            raise ValueError("Unsupported source. Use 'binance' or 'alphavantage'.")
    def fetch_alphavantage_volume_data(self, symbol="BTCUSDT", interval="5min", outputsize="compact") -> List[Dict[str, Any]]:
        """
        دریافت داده‌های حجم بازار از Alpha Vantage.
        """
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": self.alphavantage_api_key
        }
        response = requests.get(url, params=params)
        data = response.json()
        # پردازش داده‌ها به فرمت مورد نیاز
        return self.process_alphavantage_data(data)
    def process_alphavantage_data(self, data: dict) -> List[Dict[str, Any]]:
        """
        پردازش داده‌های Alpha Vantage به فرمت مورد نیاز.
        """
        time_series = data.get("Time Series (5min)", {})
        processed_data = []
        for timestamp, values in time_series.items():
            processed_data.append({
                "timestamp": timestamp,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": float(values["5. volume"]),
            })
        return processed_data
    def save_volume_data(self, symbol: str, filename: str, format: str = "csv"):
        """ ذخیره داده‌های حجم بازار به فایل.
        """
        if format == "csv":
            df = self.get_volume_trend_df(symbol)
            df.to_csv(filename, index=False)
        elif format == "json":
            json_data = self.get_volume_trend_json(symbol)
            with open(filename, "w") as f:
                f.write(json_data)
        else:
            raise ValueError("Unsupported format. Use 'csv' or 'json'.")    
    def get_market_data(self, market_name: str) -> Dict[str, Any]:
        """
        دریافت داده‌های کلی بازار به صورت دیکشنری.
        """
        if market_name not in self.markets:
            raise ValueError(f"Market {market_name} not found.")
        return self.markets[market_name]
    def get_market_data_df(self, market_name: str) -> pd.DataFrame:
        """
        دریافت داده‌های کلی بازار به صورت DataFrame.
        """
        market_data = self.get_market_data(market_name)
        return pd.DataFrame([market_data])
    def get_market_data_json(self, market_name: str) -> str:
        """ دریافت داده‌های کلی بازار به صورت JSON.
        """
        market_data = self.get_market_data(market_name)
        return json.dumps(market_data, ensure_ascii=False, indent=2)
    def get_market_data_csv(self, market_name: str, filename: str):
        """ دریافت داده‌های کلی بازار به صورت CSV.
        """
        market_data = self.get_market_data(market_name)
        df = pd.DataFrame([market_data])
        df.to_csv(filename, index=False)
    def get_market_data_dict(self, market_name: str) -> Dict[str, Any]:
        """ دریافت داده‌های کلی بازار به صورت دیکشنری.
        """
        return self.get_market_data(market_name)
    def get_market_data_list(self) -> List[Dict[str, Any]]:
        """ دریافت داده‌های کلی همه بازارها به صورت لیست دیکشنری.
        """
        return [self.get_market_data(name) for name in self.markets.keys()]
    def get_market_data_df_list(self) -> pd.DataFrame:
        """ دریافت داده‌های کلی همه بازارها به صورت DataFrame.
        """
        data_list = self.get_market_data_list()
        return pd.DataFrame(data_list)
    def get_market_data_json_list(self) -> str:
        """ دریافت داده‌های کلی همه بازارها به صورت JSON.
        """
        data_list = self.get_market_data_list()
        return json.dumps(data_list, ensure_ascii=False, indent=2)
    def get_market_data_csv_list(self, filename: str):
        """ دریافت داده‌های کلی همه بازارها به صورت CSV.
        """
        data_list = self.get_market_data_list()
        df = pd.DataFrame(data_list)
        df.to_csv(filename, index=False)
    def get_market_data_dict_list(self) -> List[Dict[str, Any]]:
        """ دریافت داده‌های کلی همه بازارها به صورت لیست دیکشنری.
        """
        return self.get_market_data_list()
    def get_market_data_dict_df(self) -> pd.DataFrame:
        """ دریافت داده‌های کلی همه بازارها به صورت DataFrame.
        """
        data_list = self.get_market_data_list()
        return pd.DataFrame(data_list)
    def get_market_data_dict_json(self) -> str:
        """ دریافت داده‌های کلی همه بازارها به صورت JSON.
        """
        data_list = self.get_market_data_list()
        return json.dumps(data_list, ensure_ascii=False, indent=2)
    def get_market_data_dict_csv(self, filename: str):
        """ دریافت داده‌های کلی همه بازارها به صورت CSV.
        """
        data_list = self.get_market_data_list()
        df = pd.DataFrame(data_list)
        df.to_csv(filename, index=False)
    def get_market_data_dict_list_json(self) -> str:
        """ دریافت داده‌های کلی همه بازارها به صورت JSON.
        """
        data_list = self.get_market_data_dict_list()
        return json.dumps(data_list, ensure_ascii=False, indent=2)
    def get_market_data_dict_list_csv(self, filename: str):
        """ دریافت داده‌های کلی همه بازارها به صورت CSV.
        """
        data_list = self.get_market_data_dict_list()
        df = pd.DataFrame(data_list)
        df.to_csv(filename, index=False)
    def get_market_data_dict_list_df(self) -> pd.DataFrame:
        """ دریافت داده‌های کلی همه بازارها به صورت DataFrame.
        """
        data_list = self.get_market_data_dict_list()
        return pd.DataFrame(data_list)
    def get_market_data_dict_list_dict(self) -> List[Dict[str, Any]]:
        """ دریافت داده‌های کلی همه بازارها به صورت لیست دیکشنری.
        """
        data_list = self.get_market_data_dict_list()
        return data_list
    def get_market_data_dict_list_csv(self, filename: str):
        """ دریافت داده‌های کلی همه بازارها به صورت CSV.
        """
        data_list = self.get_market_data_dict_list()
        df = pd.DataFrame(data_list)
        df.to_csv(filename, index=False)
    def get_market_data_dict_list_json(self) -> str:
        """ دریافت داده‌های کلی همه بازارها به صورت JSON.
        """
        data_list = self.get_market_data_dict_list()
        return json.dumps(data_list, ensure_ascii=False, indent=2)
    def get_market_data_dict_list_df(self) -> pd.DataFrame:
        """ دریافت داده‌های کلی همه بازارها به صورت DataFrame.
        """
        data_list = self.get_market_data_dict_list()
        return pd.DataFrame(data_list)
    def get_market_data_dict_list_dict(self) -> List[Dict[str, Any]]:
        """ دریافت داده‌های کلی همه بازارها به صورت لیست دیکشنری.
        """
        data_list = self.get_market_data_dict_list()
        return data_list
    def get_market_data_dict_list_csv(self, filename: str):
        """ دریافت داده‌های کلی همه بازارها به صورت CSV.
        """
        data_list = self.get_market_data_dict_list()
        df = pd.DataFrame(data_list)
        df.to_csv(filename, index=False)
    def get_market_data_dict_list_json(self) -> str:
        """ دریافت داده‌های کلی همه بازارها به صورت JSON.
        """
        data_list = self.get_market_data_dict_list()
        return json.dumps(data_list, ensure_ascii=False, indent=2)
    def get_market_data_dict_list_df(self) -> pd.DataFrame:
        """ دریافت داده‌های کلی همه بازارها به صورت DataFrame.
        """
        data_list = self.get_market_data_dict_list()
        return pd.DataFrame(data_list)
    def get_market_data_dict_list_dict(self) -> List[Dict[str, Any]]:
        """ دریافت داده‌های کلی همه بازارها به صورت لیست دیکشنری.
        """
        data_list = self.get_market_data_dict_list()
        return data_list
    def get_market_data_dict_list_csv(self, filename: str):
        """ دریافت داده‌های کلی همه بازارها به صورت CSV.
        """
        data_list = self.get_market_data_dict_list()
        df = pd.DataFrame(data_list)
        df.to_csv(filename, index=False)
    def get_market_data_dict_list_json(self) -> str:
        """ دریافت داده‌های کلی همه بازارها به صورت JSON.
        """
        data_list = self.get_market_data_dict_list()
        return json.dumps(data_list, ensure_ascii=False, indent=2)
   
    def get_sessions_in_timezone(
        self,
        target_timezone: str,
        market_name: str = None,
    ) -> list:
        """
        خروجی: لیست دیکشنری با سشن‌ها بر مبنای منطقه زمانی مقصد.
        """
        results = []
        # اروردهی اسم اشتباه بازار
        if market_name is not None and market_name not in self.markets:
            raise ValueError(f"بازار '{market_name}' پیدا نشد.")
        markets = (
            {market_name: self.markets[market_name]}
            if market_name is not None
            else self.markets
        )
        for market, info in markets.items():
            market_tz = info["timezone"]
            for session in info["sessions"]:
                now = datetime.now(pytz.timezone(market_tz))
                start_dt = now.replace(hour=session[0][0], minute=session[0][1], second=0, microsecond=0)
                end_dt   = now.replace(hour=session[1][0], minute=session[1][1], second=0, microsecond=0)
                target_start = start_dt.astimezone(pytz.timezone(target_timezone))
                target_end   = end_dt.astimezone(pytz.timezone(target_timezone))
                results.append({
                    "market": market,
                    "session_local": f"{session[0][0]:02d}:{session[0][1]:02d} - {session[1][0]:02d}:{session[1][1]:02d} ({market_tz})",
                    "session_target": f"{target_start.strftime('%H:%M')} - {target_end.strftime('%H:%M')} ({target_timezone})",
                    "session_start_target": target_start.strftime('%Y-%m-%d %H:%M'),
                    "session_end_target": target_end.strftime('%Y-%m-%d %H:%M'),
                })
        return results

    def get_sessions_in_timezone_df(
        self,
        target_timezone: str,
        market_name: str = None,
    ) -> pd.DataFrame:
        """
        خروجی: DataFrame پانداس از سشن‌ها بر اساس zone دلخواه
        """
        data = self.get_sessions_in_timezone(target_timezone, market_name)
        return pd.DataFrame(data)

    def get_sessions_in_timezone_json(
        self,
        target_timezone: str,
        market_name: str = None,
        ensure_ascii: bool = False,
        indent: int = 2,
    ) -> str:
        """
        خروجی: JSON (رشته)
        """
        data = self.get_sessions_in_timezone(target_timezone, market_name)
        return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)

    def get_sessions_in_timezone_csv(self,target_timezone: str, market_name: str = None, filename: str = "sessions.csv",
    ) -> None:
        """
        ذخیره به صورت فایل CSV در آدرس filename
        """
        df = self.get_sessions_in_timezone_df(target_timezone, market_name)
        df.to_csv(filename, index=False)
