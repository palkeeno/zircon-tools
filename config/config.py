import os
from pathlib import Path

from dotenv import load_dotenv

# 環境変数の設定
ENV = os.getenv("ENV", "development")  # デフォルトは開発環境
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 環境に応じた.envファイルを読み込む
ENV_FILE = ".env.production" if ENV == "production" else ".env.development"
load_dotenv(PROJECT_ROOT / ENV_FILE)

# 設定マネージャーのインポート
from config.settings_manager import SettingsManager

# 設定マネージャーのインスタンスを作成
settings = SettingsManager()

#### Load Env (Sensitive Information) ####
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DB_MINING = os.getenv("DB_MINING")
DB_USERS = os.getenv("DB_USERS")
CWD = os.getenv("CWD")
MCH = int(os.getenv("MCH"))

#### Load Config (Public Information) ####
# Channels
CHID_MINING = int(os.getenv("CHID_MINING"))
BRAVE_CHAT = int(os.getenv("BRAVE_CHAT"))
FREEDOM_CHAT = int(os.getenv("FREEDOM_CHAT"))
GLORY_CHAT = int(os.getenv("GLORY_CHAT"))
PEACEFUL_CHAT = int(os.getenv("PEACEFUL_CHAT"))
# 国未所属者用Excellent報告チャンネル
_MINING_EXCELLENT_CHANNEL = os.getenv("MINING_EXCELLENT_CH") or os.getenv(
    "MINING_EXCELLENT_CHAT"
)
if not _MINING_EXCELLENT_CHANNEL:
    raise RuntimeError(
        f"MINING_EXCELLENT_CH is not configured in {ENV_FILE} "
        "(legacy MINING_EXCELLENT_CHAT is also supported)"
    )
MINING_EXCELLENT_CH = int(_MINING_EXCELLENT_CHANNEL)
# 2025-11版で使用していた名前。既存の設定・参照との互換性のため残す。
MINING_EXCELLENT_CHAT = MINING_EXCELLENT_CH

# Roles
BRAVE_ROLE = int(os.getenv("BRAVE_ROLE"))
FREEDOM_ROLE = int(os.getenv("FREEDOM_ROLE"))
GLORY_ROLE = int(os.getenv("GLORY_ROLE"))
PEACEFUL_ROLE = int(os.getenv("PEACEFUL_ROLE"))
# 採掘ロール
MINING_ROLE = int(os.getenv("MINING_ROLE"))

# Emojis
BRAVE_EMOJI = os.getenv("BRAVE_EMOJI")
FREEDOM_EMOJI = os.getenv("FREEDOM_EMOJI")
GLORY_EMOJI = os.getenv("GLORY_EMOJI")
PEACEFUL_EMOJI = os.getenv("PEACEFUL_EMOJI")


# country roles id
COUNTRIES = [
    {'id':1, 'role':BRAVE_ROLE, 'name':'Brave',    'chid':BRAVE_CHAT,    'stmp':BRAVE_EMOJI}, # brave
    {'id':2, 'role':FREEDOM_ROLE, 'name':'Freedom',  'chid':FREEDOM_CHAT,    'stmp':FREEDOM_EMOJI}, # freedom
    {'id':3, 'role':GLORY_ROLE, 'name':'Glory',    'chid':GLORY_CHAT,    'stmp':GLORY_EMOJI}, # glory
    {'id':4, 'role':PEACEFUL_ROLE, 'name':'Peaceful', 'chid':PEACEFUL_CHAT,    'stmp':PEACEFUL_EMOJI}  # peaceful
]

# 設定値を動的に取得する関数
def get_mine_open():
    """鉱山の営業状況を動的に取得"""
    return settings.get_mine_open()

def get_announce_hour():
    """アナウンス時間の時を動的に取得"""
    return settings.get_announce_hour()

def get_announce_minute():
    """アナウンス時間の分を動的に取得"""
    return settings.get_announce_minute()

def get_probability():
    """採掘確率設定を動的に取得"""
    return settings.get_probability()
