from dotenv import load_dotenv
load_dotenv()

import os
import discord

#### Load Env ####
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DB_MINING = os.getenv('DB_MINING')
DB_USERS = os.getenv('DB_USERS')
CWD = os.getenv('CWD')

CHID_MINING = int(os.getenv('CHID_MINING')) # 採掘用ChID
B_CHAT = int(os.getenv('B_CHAT')) #Brave雑談チャンネルID
F_CHAT = int(os.getenv('F_CHAT')) #Freedom雑談チャンネルID
G_CHAT = int(os.getenv('G_CHAT')) #Glory雑談チャンネルID
P_CHAT = int(os.getenv('P_CHAT')) #Peaceful雑談チャンネルID
B_ROLE = int(os.getenv('B_ROLE')) #Brave所属ロールID
F_ROLE = int(os.getenv('F_ROLE')) #Freedom所属ロールID
G_ROLE = int(os.getenv('G_ROLE')) #Glory所属ロールID
P_ROLE = int(os.getenv('P_ROLE')) #Peaceful所属ロールID
MCH = int(os.getenv('MCH'))
B_EMOJI = os.getenv('B_EMOJI')
F_EMOJI = os.getenv('F_EMOJI')
G_EMOJI = os.getenv('G_EMOJI')
P_EMOJI = os.getenv('P_EMOJI')

DEBUG_CMD = os.getenv('DEBUG_CMD')
RESET_CMD = os.getenv('RESET_CMD')
MNG_CMD = os.getenv('MNG_CMD')
ADD_CMD = os.getenv('ADD_CMD')
MSG_CMD = os.getenv('MSG_CMD')
START_CMD = os.getenv('START_CMD')
STOP_CMD = os.getenv('STOP_CMD')
##################

# mining flag
MINE_OPEN = True

# announce clock
ANN_HOUR = [0,12]
ANN_MINUTE = [0]

# mining probability
PROBABILITY = [
    {'id':0,    'msg':'Excellent!!',    'prob':0.03,    'zirnum':10},
    {'id':1,    'msg':'Great!',         'prob':0.25,    'zirnum':3},
    {'id':2,    'msg':'Good',           'prob':1,       'zirnum':1}
]

# country roles id
COUNTRIES = [
    {'id':1, 'role':B_ROLE, 'name':'Brave',    'chid':B_CHAT,    'stmp':B_EMOJI}, # brave
    {'id':2, 'role':F_ROLE, 'name':'Freedom',  'chid':F_CHAT,    'stmp':F_EMOJI}, # freedom
    {'id':3, 'role':G_ROLE, 'name':'Glory',    'chid':G_CHAT,    'stmp':G_EMOJI}, # glory
    {'id':4, 'role':P_ROLE, 'name':'Peaceful', 'chid':P_CHAT,    'stmp':P_EMOJI}  # peaceful
]