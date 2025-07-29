# print(DateRangeParser.parse("LAST_1_DAYS"))
# print(DateRangeParser.parse("LAST_2_DAYS"))
# print(DateRangeParser.parse(DateRangeType.CUSTOM, start_date='2025-04-01', end_date='2025-04-05'))
#
# print(DateRangeParser.parse("LAST_MONTH"))
# print(DateRangeParser.parse(DateRangeType.EACH_MONTH, start_date='2025-04-01', end_date='2025-04-05'))
from datetime import datetime, timedelta

from xfit_rpa.utils.date_util import DateRangeParser, DateRangeType, date_to_str


def test_last_n_days():
    result = DateRangeParser.parse("LAST_7_DAYS")
    assert len(result) == 1
    assert isinstance(result[0][0], str)


def test_each_day():
    result = DateRangeParser.parse("EACH_DAY", "2024-01-01", "2024-01-03")
    assert len(result) == 3
    assert result[0][0] == "2024-01-01"


def test_date_range_last_month():
    today = datetime.now()
    last_day_of_month = today.replace(day=1) - timedelta(days=1)
    first_day_of_month = last_day_of_month.replace(day=1)
    result = DateRangeParser.parse("LAST_MONTH")
    assert result == [(date_to_str(first_day_of_month), date_to_str(last_day_of_month))]  # 这里的结果可能需要根据实际逻辑调整


def test_date_range_each_month():
    result = DateRangeParser.parse(DateRangeType.EACH_MONTH, start_date='2025-04-01', end_date='2025-05-05')
    assert result == [('2025-04-01', '2025-04-30'), ('2025-05-01', '2025-05-05')]  # 这里的结果可能需要根据实际逻辑调整


def test_date_range_custom():
    result = DateRangeParser.parse(DateRangeType.CUSTOM, start_date='2025-04-01', end_date='2025-04-05')
    assert result[0][0] == '2025-04-01'
    assert result == [('2025-04-01', '2025-04-05')]  # 这里的结果可能需要根据实际逻辑调整
