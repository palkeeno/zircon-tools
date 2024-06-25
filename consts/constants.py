from datetime import timedelta, timezone

from config import CWD

# timezone
JST = timezone(timedelta(hours=+9), "JST")

# datetime <-> String の変換フォーマット(ISO)
LONG_DT_FORMAT = "%Y-%m-%d %H:%M:%S"
SHORT_DT_FORMAT = "%Y-%m-%d"

# csv header
RANK_HEADER = [
    "順位",
    "ユーザ名",
    "採掘数",
    "国名",
    "採掘回数",
    "Excellent回数",
    "メンションid",
]

# folder path
CSV_FOLDER = CWD + "/csv/"

# exetention
CSV = ".csv"
