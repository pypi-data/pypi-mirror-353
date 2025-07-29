# utils/date_utils.py
from datetime import datetime, timedelta, date
from enum import Enum, auto
from typing import Optional, Union, List, Tuple

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# ========================
# 基础转换函数
# ========================

def now() -> datetime:
    return datetime.now()


def today() -> date:
    return date.today()


def str_to_date(s: str, fmt: str = DATE_FORMAT) -> date:
    return datetime.strptime(s, fmt).date()


def str_to_datetime(s: str, fmt: str = DATETIME_FORMAT) -> datetime:
    return datetime.strptime(s, fmt)


def date_to_str(d: Union[date, datetime], fmt: str = DATE_FORMAT) -> str:
    return d.strftime(fmt)


def datetime_to_str(dt: datetime, fmt: str = DATETIME_FORMAT) -> str:
    return dt.strftime(fmt)


# ========================
# 日期加减
# ========================

def add_days(d: Union[date, datetime], days: int) -> Union[date, datetime]:
    return d + timedelta(days=days)


def add_hours(dt: datetime, hours: int) -> datetime:
    return dt + timedelta(hours=hours)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    return dt + timedelta(minutes=minutes)


# ========================
# 起止时间
# ========================

def start_of_day(dt: Union[date, datetime]) -> datetime:
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time())
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: Union[date, datetime]) -> datetime:
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.max.time())
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def start_of_month(dt: Union[date, datetime]) -> datetime:
    return start_of_day(dt.replace(day=1))


def end_of_month(dt: Union[date, datetime]) -> datetime:
    next_month = dt.replace(day=28) + timedelta(days=4)
    return end_of_day(next_month.replace(day=1) - timedelta(days=1))


# ========================
# 时间差计算
# ========================

def days_between(start: date, end: date) -> int:
    return (end - start).days


def seconds_between(start: datetime, end: datetime) -> int:
    return int((end - start).total_seconds())


# ========================
# 其他
# ========================

def is_same_day(dt1: Union[date, datetime], dt2: Union[date, datetime]) -> bool:
    return dt1.date() == dt2.date()


def get_weekday(d: Union[date, datetime]) -> int:
    # 返回 0=周一, ..., 6=周日
    return d.weekday()


def is_weekend(d: Union[date, datetime]) -> bool:
    return d.weekday() >= 5


class DateRangeType(Enum):
    EACH_DAY = auto()
    EACH_MONTH = auto()
    LAST_N_DAYS = auto()
    LAST_MONTH = auto()
    CUSTOM = auto()


class DateRangeParser:

    @staticmethod
    def parse(
            date_type: Union[str, DateRangeType],
            start_date: Optional[Union[datetime, str]] = None,
            end_date: Optional[Union[datetime, str]] = None,
            n_days: Optional[int] = None,
            date_format: Optional[str] = DATE_FORMAT
    ) -> List[Tuple[Union[datetime, str], Union[datetime, str]]]:

        # 标准化类型
        date_type, n_days = DateRangeParser._normalize_type(date_type, n_days)
        today = datetime.today()

        # 解析字符串为 datetime
        start_date = DateRangeParser._parse_datetime(start_date, date_format)
        end_date = DateRangeParser._parse_datetime(end_date, date_format)

        # 校验顺序
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")

        # 选择对应逻辑
        if date_type == DateRangeType.EACH_DAY:
            ranges = DateRangeParser._each_day(start_date, end_date)
        elif date_type == DateRangeType.EACH_MONTH:
            ranges = DateRangeParser._each_month(start_date, end_date)
        elif date_type == DateRangeType.LAST_N_DAYS:
            ranges = DateRangeParser._last_n_days(today, n_days)
        elif date_type == DateRangeType.LAST_MONTH:
            ranges = DateRangeParser._last_month(today)
        elif date_type == DateRangeType.CUSTOM:
            if not start_date or not end_date:
                raise ValueError("start_date and end_date must be provided for CUSTOM")
            ranges = [(start_date, end_date)]
        else:
            raise ValueError(f"Unsupported date type: {date_type}")

        # 格式化输出
        if date_format:
            ranges = [(d1.strftime(date_format), d2.strftime(date_format)) for d1, d2 in ranges]
        return ranges

    # ========= 子方法 =========

    @staticmethod
    def _normalize_type(date_type: Union[str, DateRangeType], n_days: Optional[int]) -> Tuple[
        DateRangeType, Optional[int]]:
        if isinstance(date_type, str):
            if date_type.startswith("LAST_") and date_type.endswith("_DAYS"):
                try:
                    n_days = int(date_type.split("_")[1])
                    return DateRangeType.LAST_N_DAYS, n_days
                except Exception:
                    raise ValueError("Invalid format for LAST_N_DAYS. Expected like 'LAST_30_DAYS'.")
            try:
                return DateRangeType[date_type], n_days
            except KeyError:
                raise ValueError(f"Invalid date type. Valid types: {[e.name for e in DateRangeType]}")
        return date_type, n_days

    @staticmethod
    def _parse_datetime(dt: Optional[Union[datetime, str]], fmt: str) -> Optional[datetime]:
        if isinstance(dt, str):
            return datetime.strptime(dt, fmt)
        return dt

    @staticmethod
    def _each_day(start: datetime, end: datetime) -> List[Tuple[datetime, datetime]]:
        if not start or not end:
            raise ValueError("start_date and end_date must be provided for EACH_DAY")
        result = []
        current = start
        while current <= end:
            result.append((current, current))
            current += timedelta(days=1)
        return result

    @staticmethod
    def _each_month(start: datetime, end: datetime) -> List[Tuple[datetime, datetime]]:
        if not start or not end:
            raise ValueError("start_date and end_date must be provided for EACH_MONTH")
        result = []
        current = start.replace(day=1)
        while current <= end:
            next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
            last_day = next_month - timedelta(days=1)
            result.append((current, min(last_day, end)))
            current = next_month
        return result

    @staticmethod
    def _last_n_days(today: datetime, n_days: int) -> List[Tuple[datetime, datetime]]:
        if not n_days:
            raise ValueError("n_days must be provided for LAST_N_DAYS")
        end = today - timedelta(days=1)
        start = today - timedelta(days=n_days)
        return [(start, end)]

    @staticmethod
    def _last_month(today: datetime) -> List[Tuple[datetime, datetime]]:
        last_day = today.replace(day=1) - timedelta(days=1)
        first_day = last_day.replace(day=1)
        return [(first_day, last_day)]
