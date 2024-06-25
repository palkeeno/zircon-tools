from datetime import timedelta, timezone

from config import CWD

# timezone
JST = timezone(timedelta(hours=+9), "JST")

# datetime <-> String の変換フォーマット(ISO)
LONG_DT_FORMAT = "%Y-%m-%d %H:%M:%S"
SHORT_DT_FORMAT = "%Y-%m-%d"

# Constant Command sentences
CURRENT = "current"
LIFETIME = "lifetime"

# csv header
RANK_HEADER_NOW = [
    "順位",
    "ユーザ名",
    "メンションid",
    "国名",
    "採掘量(今回)",
    "採掘回数(今回)",
    "Excellent回数(今回)",
]

RANK_HEADER_LIFETIME = [
    "順位",
    "ユーザ名",
    "メンションid",
    "採掘量(累積)",
    "採掘回数(累積)",
    "Excellent回数(累積)",
]

# folder path
CSV_FOLDER = CWD + "/csv/"

# exetention
CSV = ".csv"
