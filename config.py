from dotenv import load_dotenv
load_dotenv()

import os
import discord

#### Load Env ####
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DB_MINING = os.getenv('DB_NAME')
CHID_MINING = int(os.getenv('CHID_MINING')) # 採掘用ChID
B_CHAT = int(os.getenv('B_CHAT'))
F_CHAT = int(os.getenv('F_CHAT'))
G_CHAT = int(os.getenv('G_CHAT'))
P_CHAT = int(os.getenv('P_CHAT'))
B_ROLE = int(os.getenv('B_ROLE'))
F_ROLE = int(os.getenv('F_ROLE'))
G_ROLE = int(os.getenv('G_ROLE'))
P_ROLE = int(os.getenv('P_ROLE'))
##################

# cooldown time
CD_MINING = 30

# mining result
RESULTS = [
    {'id':0,    'msg':'Excellent!!',    'prob':0.03,    'zirnum':10},
    {'id':1,    'msg':'Great!',         'prob':0.25,    'zirnum':3},
    {'id':2,    'msg':'Good',           'prob':1,       'zirnum':1}
]

# imgs
BRAVE_FLAG = discord.File("./assets/Brave.jpg", filename="Brave.jpg")
FREEDOM_FLAG = discord.File("./assets/Freedom.jpg", filename="Freedom.jpg")
GLORY_FLAG = discord.File("./assets/Glory.jpg", filename="Glory.jpg")
PEACEFUL_FLAG = discord.File("./assets/Peaceful.jpg", filename="Peaceful.jpg")

# country roles id
# TODO: 本番ではidとchidを変更する, 同時に国旗ファイル名も変える
COUNTRYS = [
    {'id':B_ROLE, 'name':'Brave',    'chid':B_CHAT,    'stmp':':B_:',   'img':BRAVE_FLAG}, # brave
    {'id':F_ROLE, 'name':'Freedom',  'chid':F_CHAT,    'stmp':':F_:',   'img':FREEDOM_FLAG}, # freedom
    {'id':G_ROLE, 'name':'Glory',    'chid':G_CHAT,    'stmp':':G_:',   'img':GLORY_FLAG}, # glory
    {'id':P_ROLE, 'name':'Peaceful', 'chid':P_CHAT,    'stmp':':P_:',   'img':PEACEFUL_FLAG}  # peaceful
]

MSG_LETS_MINING = "今日も元気に採掘しましょう！ :gem:"
MSG_ONCE_MINING = '今日の採掘は完了しています！また明日来てね！'