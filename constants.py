import datetime
from zoneinfo import ZoneInfo

MAX_PASS_COUNT = 2

# 고정된 마감일 목록
DUE_DATES = [
    datetime.datetime(
        2025, 5, 1, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")
    ),  # 준비회차 (한국시간 05:00)
    datetime.datetime(2025, 5, 13, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 0회차
    datetime.datetime(2025, 5, 20, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 1회차
    datetime.datetime(2025, 5, 27, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 2회차
    datetime.datetime(2025, 6, 3, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 3회차
    datetime.datetime(2025, 6, 10, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 4회차
    datetime.datetime(2025, 6, 17, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 5회차
    datetime.datetime(2025, 6, 24, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 6회차
    datetime.datetime(2025, 7, 1, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 7회차
    datetime.datetime(2025, 7, 8, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 8회차
    datetime.datetime(2025, 7, 15, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 9회차
    datetime.datetime(2025, 7, 22, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 10회차
    datetime.datetime(2025, 7, 29, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 11회차
    datetime.datetime(2025, 8, 5, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 12회차
    datetime.datetime(2025, 8, 12, 5, 0, 0, tzinfo=ZoneInfo("Asia/Seoul")),  # 추가회차
]

# 각 마감일의 설명
SESSION_NAMES = [
    "준비회차",
    "0회차",
    "1회차",
    "2회차",
    "3회차",
    "4회차",
    "5회차",
    "6회차",
    "7회차",
    "8회차",
    "9회차",
    "10회차",
    "11회차",
    "12회차",
    "추가회차",
]