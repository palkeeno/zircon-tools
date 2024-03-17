import config
import csv

# ガチャシステム
def gacha(rval, conf):
    # print(rval)
    for item in conf:
        if rval < item['prob']:
            return item

# 送信者の国ロールを取得する
def get_country(user):
    for usr_role in user.roles:
        for role in config.COUNTRIES:
            if usr_role.id == role['id']:
                return role
    return None

def write_csv(filename, header, data):
    with open(filename, 'w', newline="") as f:
        writer = csv.writer(f)
        if header != None:
            writer.writerow(header)
        writer.writerows(data)