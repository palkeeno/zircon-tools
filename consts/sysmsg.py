LETS_MINING = "今日も元気に採掘しましょう！ :gem:"
ONCE_MINING = "採掘は完了しています！ 採掘は毎日0時と12時にできるよ :pick:"
COUNTRY_ROLE = "どこか一つの国に所属してからまた来てね！"
MINE_CLOSED = "現在採掘所は営業を停止しております。再開されたらまたお願いします :pick:"
MANUAL_ANNOUNCE = "アナウンスを発動しました"
RESET_DB = "データベースをリセットしました"
DATA_NOT_FOUND = "データがありません"

# エラーメッセージ
ERROR_MESSAGES = {
    'DB_ERROR': 'データベース操作中にエラーが発生しました。',
    'PERMISSION_ERROR': '権限が不足しています。',
    'INVALID_AMOUNT': '無効な数値が指定されました。',
    'USER_NOT_FOUND': '指定されたユーザーが見つかりません。',
    'MINING_CLOSED': '現在採掘は停止中です。',
    'SYSTEM_ERROR': 'システムエラーが発生しました。',
}

# 動的メッセージ生成
import config

def _format_announce_times(hours, minutes):
    """設定の時・分から日本語表記の時間列を生成

    例: hours=[1,13], minutes=[30] -> "毎日1:30と13:30に"
        hours=[0,12], minutes=[0,30] -> "毎日0:00と0:30と12:00と12:30に"
    """
    try:
        uniq_hours = sorted(set(int(h) for h in (hours or [])))
        uniq_minutes = sorted(set(int(m) for m in (minutes or [])))
        # カルテシアン積で全時刻を作成
        times = [(h, m) for h in uniq_hours for m in uniq_minutes]
        # フォールバック（設定が空の場合は 0:00）
        if not times:
            times = [(0, 0)]
        # 昇順整列
        times.sort(key=lambda x: (x[0], x[1]))
        # 表記整形（分はゼロ詰め2桁）
        labels = [f"{h}:{m:02d}" for h, m in times]
        return "毎日" + "と".join(labels) + "に"
    except Exception:
        # 失敗時はデフォルト表記
        return "毎日0時と12時に"

def get_once_mining_message():
    """採掘済み時の動的メッセージを返す"""
    hours = config.get_announce_hour()
    minutes = config.get_announce_minute()
    times_text = _format_announce_times(hours, minutes)
    return f"採掘は完了しています！ 採掘は{times_text}できるよ :pick:"