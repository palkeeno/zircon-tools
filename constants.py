from datetime import timezone, timedelta
from config import CWD

# messages
MSG_LETS_MINING = "今日も元気に採掘しましょう！ :gem:"
MSG_ONCE_MINING = "採掘は完了しています！ 採掘は毎日0時と12時にできるよ :pick:"
MSG_COUNTRY_ROLE = "どこか一つの国に所属してからまた来てね！"
MSG_MINE_CLOSED = "現在採掘所は営業を停止しております。再開されたらまたお願いします :pick:"

# timezone
JST = timezone(timedelta(hours=+9), "JST")

# datetime <-> String の変換フォーマット(ISO)
LONG_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
SHORT_DT_FORMAT = '%Y-%m-%d'

# csv header
RANK_HEADER = ["順位","ユーザ名","採掘数","国名","採掘回数","Excellent回数","メンションid"]

# folder path
CSV_FOLDER = CWD+"/csv/"

# exetention
CSV = ".csv"