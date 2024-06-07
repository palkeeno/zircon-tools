import config
import discord

E001_INVALID_CHANNEL = {'code':'001', 'msg':"Error 001: Invalid channel to use this command"}
E002_INVALID_ROLE = {'code':'002', 'msg':"Error 002: Invalid roles"}
E003_DATA_NOT_FOUND = {'code':'003', 'msg':"Error 003: Data not found"}

def check_country(country):
    # 国ロールがない場合はエラー
    if country == None:
        return True
    return False
    
