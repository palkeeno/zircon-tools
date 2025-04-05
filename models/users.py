import datetime
import sqlite3

import util
from config import COUNTRIES, DB_USERS
from consts.const import CURRENT, JST, LIFETIME, LONG_DT_FORMAT
from models.db_utils import (
    init_db, get_single_record, upsert_record, reset_db, get_rank, get_current_datetime
)


# 国を無視した個人の採掘累計のテーブル作成
### current_total: 現在のzirnum合計（消費する可能性を考慮）
### lifetime_total: 生涯の合計zirnum（消費してもここからは減らさない）
### m_cnt, ex_cnt: 生涯の採掘回数合計、EX回数合計（消費しないのでlt）
async def create_db():
    # テーブルスキーマ
    schema = """
    (
        id INTEGER primary key autoincrement,
        userid INTEGER,
        curr_total INTEGER,
        lt_total INTEGER,
        m_cnt INTEGER,
        ex_cnt INTEGER,
        updated_at TEXT
    )
    """
    # データベースを初期化
    is_new = await init_db(DB_USERS, "USERS", schema, init_country_record)
    return is_new


# 国ユーザを初期で作成する
def init_country_record():
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            now = get_current_datetime()
            for country in COUNTRIES:
                cursor.execute(
                    """
                    INSERT INTO USERS(userid, curr_total, lt_total, m_cnt, ex_cnt, updated_at)
                    VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (country["id"], 0, 0, 0, 0, now),
                )
            connection.commit()
    except sqlite3.Error as e:
        print("DB-USERS INIT ERROR: ", e)


# ユーザの採掘情報を取得する
async def get_single(userid):
    return await get_single_record(DB_USERS, "USERS", userid)


# 採掘情報を更新または挿入する
async def upsert(userid, zirnum, isExcellent, isMining=True):
    now = get_current_datetime()
    
    # 既存レコードを取得
    record = await get_single(userid)
    
    if record:
        # 既存レコードを更新
        data = {
            "curr_total": record[2] + zirnum,
            "lt_total": record[3] + zirnum,
            "m_cnt": record[4] + (1 if isMining else 0),
            "ex_cnt": record[5] + (1 if isExcellent else 0),
            "updated_at": now
        }
        return await upsert_record(DB_USERS, "USERS", userid, data)
    else:
        # 新規レコードを作成
        data = {
            "curr_total": zirnum,
            "lt_total": zirnum,
            "m_cnt": 1 if isMining else 0,
            "ex_cnt": 1 if isExcellent else 0,
            "updated_at": now
        }
        return await upsert_record(DB_USERS, "USERS", userid, data)


# ランキングを取得する
async def get_rank(rank_type):
    return await get_rank(DB_USERS, "USERS", rank_type)


# データベースをリセットする
async def reset_db():
    return await reset_db(DB_USERS, "USERS")
