import config
import csv
import datetime

# ガチャシステム
def gacha(rval, conf):
    for item in conf:
        if rval < item['prob']:
            return item

# 送信者の国ロールを取得する
def get_country(user):
    if user == None:
        return None
    for usr_role in user.roles:
        for country in config.COUNTRIES:
            if usr_role.id == country['role']:
                return country
    return None

# roleid から country を特定
def get_country_by_roleid(roleid):
    if roleid == None:
        return None
    for country in config.COUNTRIES:
        if roleid == country['role']:
            return country
    return None
def write_csv(filename, header, data):
    with open(filename, 'w', newline="") as f:
        writer = csv.writer(f)
        if header != None:
            writer.writerow(header)
        writer.writerows(data)# datetime型からString型に変換
def convertDt2Str(dt:datetime):
    return dt.strftime(dt_format)
# datetime型からString型に変換
def convertDt2Str(dt:datetime, format):
    return dt.strftime(format)

# String型からdatetime型に変換
def convertStr2Dt(dt:str, format):
    return datetime.datetime.strptime(dt, format)