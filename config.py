from dotenv import load_dotenv
load_dotenv()

import os
import discord

#### Load Env ####
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DB_MINING = os.getenv('DB_NAME')

CHID_MINING = int(os.getenv('CHID_MINING')) # 採掘用ChID
B_CHAT = int(os.getenv('B_CHAT')) #Brave雑談チャンネルID
F_CHAT = int(os.getenv('F_CHAT')) #Freedom雑談チャンネルID
G_CHAT = int(os.getenv('G_CHAT')) #Glory雑談チャンネルID
P_CHAT = int(os.getenv('P_CHAT')) #Peaceful雑談チャンネルID
B_ROLE = int(os.getenv('B_ROLE')) #Brave所属ロールID
F_ROLE = int(os.getenv('F_ROLE')) #Freedom所属ロールID
G_ROLE = int(os.getenv('G_ROLE')) #Glory所属ロールID
P_ROLE = int(os.getenv('P_ROLE')) #Peaceful所属ロールID
B_EMOJI = os.getenv('B_EMOJI')
F_EMOJI = os.getenv('F_EMOJI')
G_EMOJI = os.getenv('G_EMOJI')
P_EMOJI = os.getenv('P_EMOJI')

DEBUG_CMD = os.getenv('DEBUG_CMD')
RESET_CMD = os.getenv('RESET_CMD')
VIEW_CMD = os.getenv('VIEW_CMD')
##################

# announce clock
ANN_HOUR = 0
ANN_MINUTE = 0

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
COUNTRIES = [
    {'id':B_ROLE, 'name':'Brave',    'chid':B_CHAT,    'stmp':B_EMOJI,   'img':BRAVE_FLAG}, # brave
    {'id':F_ROLE, 'name':'Freedom',  'chid':F_CHAT,    'stmp':F_EMOJI,   'img':FREEDOM_FLAG}, # freedom
    {'id':G_ROLE, 'name':'Glory',    'chid':G_CHAT,    'stmp':G_EMOJI,   'img':GLORY_FLAG}, # glory
    {'id':P_ROLE, 'name':'Peaceful', 'chid':P_CHAT,    'stmp':P_EMOJI,   'img':PEACEFUL_FLAG}  # peaceful
]

MSG_LETS_MINING = "今日も元気に採掘しましょう！ :gem:"
MSG_ONCE_MINING = '今日の採掘は完了しています！また明日来てね！'
MSG_COUNTRY_ROLE = 'どこか一つの国に所属してからまた来てね！'