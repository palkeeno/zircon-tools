import sqlite3

import config.config as config
from utils.db_utils import (
    init_db, get_single_record, upsert_record, reset_db as reset_db_table, get_rank, get_current_datetime, handle_db_error
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
    is_new = await init_db(config.DB_USERS, "USERS", schema, init_country_record)
    return is_new


# 国ユーザを初期で作成する
def init_country_record():
    try:
        with sqlite3.connect(config.DB_USERS) as connection:
            cursor = connection.cursor()
            now = get_current_datetime()
            for country in config.COUNTRIES:
                cursor.execute(
                    """
                    INSERT INTO USERS(userid, curr_total, lt_total, m_cnt, ex_cnt, updated_at)
                    VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (country["id"], 0, 0, 0, 0, now),
                )
            connection.commit()
    except sqlite3.Error as e:
        handle_db_error(e, "INIT", config.DB_USERS)


# ユーザの採掘情報を取得する
async def get_single(userid):
    return await get_single_record(config.DB_USERS, "USERS", userid)


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
        return await upsert_record(config.DB_USERS, "USERS", userid, data)
    else:
        # 新規レコードを作成
        data = {
            "curr_total": zirnum,
            "lt_total": zirnum,
            "m_cnt": 1 if isMining else 0,
            "ex_cnt": 1 if isExcellent else 0,
            "updated_at": now
        }
        return await upsert_record(config.DB_USERS, "USERS", userid, data)


# ランキングを取得する
async def get_rank(rank_type):
    return await get_rank(config.DB_USERS, "USERS", rank_type)


# データベースをリセットする
async def reset_db():
    return await reset_db_table(config.DB_USERS, "USERS")


# 全ユーザーの統計情報を取得する
async def get_all_stats():
    try:
        with sqlite3.connect(config.DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT userid, curr_total, updated_at
                FROM USERS
                ORDER BY curr_total DESC
                """
            )
            results = cursor.fetchall()
            
            # 統計情報のリストを作成
            stats = []
            for userid, total, last_mined in results:
                # 国情報を取得
                country = "不明"
                for c in config.COUNTRIES:
                    if userid == c["id"]:
                        country = c["name"]
                        break
                
                stats.append({
                    "user_id": userid,
                    "country": country,
                    "total_amount": total,
                    "last_mined": last_mined
                })
            return stats
    except sqlite3.Error as e:
        handle_db_error(e, "GET_ALL_STATS", config.DB_USERS)
        return []


# 全ユーザーの生涯統計情報を取得する
async def get_all_lifetime_stats(guild):
    try:
        with sqlite3.connect(config.DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT userid, lt_total, m_cnt, ex_cnt
                FROM USERS
                ORDER BY lt_total DESC
                """
            )
            results = cursor.fetchall()
            
            # 統計情報のリストを作成
            stats = []
            for userid, lt_total, m_cnt, ex_cnt in results:
                # ユーザー情報を取得
                user = guild.get_member(userid)
                username = user.display_name if user else "不明"
                mention = user.mention if user else f"<@{userid}>"
                
                stats.append({
                    "user_id": userid,
                    "username": username,
                    "mention": mention,
                    "lt_total": lt_total,
                    "m_cnt": m_cnt,
                    "ex_cnt": ex_cnt
                })
            return stats
    except sqlite3.Error as e:
        handle_db_error(e, "GET_ALL_LIFETIME_STATS", config.DB_USERS)
        return []
