import os
from dotenv import load_dotenv

# 環境変数の設定
ENV = os.getenv("ENV", "development")  # デフォルトは開発環境

# 環境に応じた.envファイルを読み込む
if ENV == "production":
    load_dotenv(".env.production")
else:
    load_dotenv(".env.development")

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

# mining flag
MINE_OPEN = True

# announce clock
# TODO: This will changable from discord ui
ANN_HOUR = [0, 12]
ANN_MINUTE = [0]

# mining probability
PROBABILITY = [
    {'id':0,    'msg':'Excellent',    'prob':0.03,    'zirnum':10},
    {'id':1,    'msg':'Great',         'prob':0.25,    'zirnum':3},
    {'id':2,    'msg':'Good',           'prob':1,       'zirnum':1}
]

# country roles id
COUNTRIES = [
    {'id':1, 'role':BRAVE_ROLE, 'name':'Brave',    'chid':BRAVE_CHAT,    'stmp':BRAVE_EMOJI}, # brave
    {'id':2, 'role':FREEDOM_ROLE, 'name':'Freedom',  'chid':FREEDOM_CHAT,    'stmp':FREEDOM_EMOJI}, # freedom
    {'id':3, 'role':GLORY_ROLE, 'name':'Glory',    'chid':GLORY_CHAT,    'stmp':GLORY_EMOJI}, # glory
    {'id':4, 'role':PEACEFUL_ROLE, 'name':'Peaceful', 'chid':PEACEFUL_CHAT,    'stmp':PEACEFUL_EMOJI}  # peaceful
]