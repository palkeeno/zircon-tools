import config

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