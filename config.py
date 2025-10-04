import os
from dotenv import load_dotenv

# 環境変数の設定
ENV = os.getenv("ENV", "development")  # デフォルトは開発環境

# 環境に応じた.envファイルを読み込む
if ENV == "production":
    load_dotenv(".env.production")
else:
    load_dotenv(".env.development")

# 設定マネージャーのインポート
from settings_manager import settings_manager

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

# Roles
BRAVE_ROLE = int(os.getenv("BRAVE_ROLE"))
FREEDOM_ROLE = int(os.getenv("FREEDOM_ROLE"))
GLORY_ROLE = int(os.getenv("GLORY_ROLE"))
PEACEFUL_ROLE = int(os.getenv("PEACEFUL_ROLE"))

# Emojis
BRAVE_EMOJI = os.getenv("BRAVE_EMOJI")
FREEDOM_EMOJI = os.getenv("FREEDOM_EMOJI")
GLORY_EMOJI = os.getenv("GLORY_EMOJI")
PEACEFUL_EMOJI = os.getenv("PEACEFUL_EMOJI")

# mining flag (設定マネージャーから取得)
MINE_OPEN = settings_manager.get_mine_open()

# announce clock (設定マネージャーから取得)
ANN_HOUR = settings_manager.get_announce_hour()
ANN_MINUTE = settings_manager.get_announce_minute()

# mining probability (設定マネージャーから取得)
PROBABILITY = settings_manager.get_probability()

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
    return settings_manager.get_mine_open()

def get_announce_hour():
    """アナウンス時間の時を動的に取得"""
    return settings_manager.get_announce_hour()

def get_announce_minute():
    """アナウンス時間の分を動的に取得"""
    return settings_manager.get_announce_minute()

def get_probability():
    """採掘確率設定を動的に取得"""
    return settings_manager.get_probability()