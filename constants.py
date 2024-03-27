from datetime import timezone, timedelta

# messages
MSG_LETS_MINING = "今日も元気に採掘しましょう！ :gem:"
MSG_ONCE_MINING = "採掘は完了しています！ 採掘は毎日0時と12時にできるよ :pick:"
MSG_COUNTRY_ROLE = "どこか一つの国に所属してからまた来てね！"

# timezone
JST = timezone(timedelta(hours=+9), "JST")

# datetime <-> String の変換フォーマット(ISO)
LONG_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
SHORT_DT_FORMAT = '%Y-%m-%d'

RANK_HEADER = ["順位","ユーザ名","採掘ジルコン","国名","採掘回数","Excellent回数"]