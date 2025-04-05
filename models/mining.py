import datetime
import sqlite3

import util
from config import COUNTRIES, DB_MINING
from consts.const import JST, LONG_DT_FORMAT
from models.db_utils import (
    init_db, get_single_record, upsert_record, reset_db, get_rank, get_current_datetime
)


# 採掘結果のテーブル作成
### zirnum = number of mined zircon
### m_cnt = total count of mining as this user
### ex_cnt = total count of excellent as this user
### done_flag = the flag of wheather this user have done mining or not, 0:Flase, 1:True
async def create_db():
    # テーブルスキーマ
    schema = """
    (
        id INTEGER primary key autoincrement,
        userid INTEGER,
        roleid INTEGER,
        zirnum INTEGER,
        m_cnt INTEGER,
        ex_cnt INTEGER,
        done_flag INTEGER,
        updated_at TEXT
    )
    """
    # データベースを初期化
    is_new = await init_db(DB_MINING, "MINING", schema, init_country_record)
    return is_new


# 国ユーザを初期で作成する
def init_country_record():
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            now = get_current_datetime()
            for country in COUNTRIES:
                cursor.execute(
                    """
                    INSERT INTO MINING(userid, roleid, zirnum, m_cnt, ex_cnt, done_flag, updated_at)
                    VALUES(?, ?, ?, ?, ?, ?, ?)
                    """,
                    (country["id"], country["role"], 0, 0, 0, 0, now),
                )
            connection.commit()
    except sqlite3.Error as e:
        print("DB-MINING INIT ERROR: ", e)


# 採掘済みフラグをリセットする
async def undo_done_flag():
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE MINING SET done_flag = 0")
            connection.commit()
    except sqlite3.Error as e:
        print("DB-MINING UNDO ERROR: ", e)


# ユーザの採掘情報を取得する
async def get_user_single(userid, roleid):
    return await get_single_record(DB_MINING, "MINING", userid, roleid)


# 国の採掘情報を取得する
async def get_country_single(roleid):
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT roleid, SUM(zirnum) as total_zirnum, COUNT(*) as total_count
                FROM MINING
                WHERE roleid = ?
                GROUP BY roleid
                """,
                (roleid,),
            )
            return cursor.fetchone()
    except sqlite3.Error as e:
        print("DB-MINING GET COUNTRY ERROR: ", e)
        return None


# 採掘情報を更新または挿入する
async def upsert(userid, roleid, zirnum, isExcellent, done_flag=1):
    now = get_current_datetime()
    
    # 既存レコードを取得
    record = await get_user_single(userid, roleid)
    
    if record:
        # 既存レコードを更新
        data = {
            "zirnum": record[3] + zirnum,
            "m_cnt": record[4] + 1,
            "ex_cnt": record[5] + (1 if isExcellent else 0),
            "done_flag": done_flag,
            "updated_at": now
        }
        return await upsert_record(DB_MINING, "MINING", userid, data, roleid)
    else:
        # 新規レコードを作成
        data = {
            "zirnum": zirnum,
            "m_cnt": 1,
            "ex_cnt": 1 if isExcellent else 0,
            "done_flag": done_flag,
            "updated_at": now
        }
        return await upsert_record(DB_MINING, "MINING", userid, data, roleid)


# 国内ユーザランキングを取得する
async def get_rank_user_country(roleid):
    return await get_rank(DB_MINING, "MINING", "user_country", roleid)


# 全ユーザランキングを取得する
async def get_rank_user_overall():
    return await get_rank(DB_MINING, "MINING", "user_overall")


# 国ランキングを取得する
async def get_country_each():
    return await get_rank(DB_MINING, "MINING", "country")


# データベースをリセットする
async def reset_db():
    return await reset_db(DB_MINING, "MINING")
