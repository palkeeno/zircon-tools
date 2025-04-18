import sqlite3

import config
from models.db_utils import (
    init_db, get_single_record, upsert_record, reset_db as reset_db_table, get_rank, get_current_datetime, handle_db_error
)
import util


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
        roleid INTEGER,
        zirnum INTEGER,
        m_cnt INTEGER,
        ex_cnt INTEGER,
        done_flag INTEGER,
        updated_at TEXT
    )
    """
    # データベースを初期化
    is_new = await init_db(config.DB_MINING, "MINING", schema, init_country_record)
    return is_new


# 国ユーザを初期で作成する
def init_country_record():
    try:
        with sqlite3.connect(config.DB_MINING) as connection:
            cursor = connection.cursor()
            now = get_current_datetime()
            for country in config.COUNTRIES:
                cursor.execute(
                    """
                    INSERT INTO MINING(userid, roleid, zirnum, m_cnt, ex_cnt, done_flag, updated_at)
                    VALUES(?, ?, ?, ?, ?, ?, ?)
                    """,
                    (country["id"], country["role"], 0, 0, 0, 0, now),
                )
            connection.commit()
    except sqlite3.Error as e:
        handle_db_error(e, "INIT", config.DB_MINING)


# 採掘済みフラグをリセットする
async def undo_done_flag():
    try:
        with sqlite3.connect(config.DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE MINING
                SET done_flag = 0
                """
            )
            connection.commit()
    except sqlite3.Error as e:
        handle_db_error(e, "UNDO_DONE_FLAG", config.DB_MINING)


# ユーザの採掘情報を取得する
async def get_user_single(userid, roleid):
    return await get_single_record(config.DB_MINING, "MINING", userid, roleid)


# 国の採掘情報を取得する
async def get_country_single(roleid):
    try:
        with sqlite3.connect(config.DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT roleid, SUM(zirnum), COUNT(*)
                FROM MINING
                WHERE roleid = ?
                GROUP BY roleid
                """,
                (roleid,),
            )
            return cursor.fetchone()
    except sqlite3.Error as e:
        handle_db_error(e, "GET_COUNTRY_SINGLE", config.DB_MINING)
        return None


# 採掘情報を更新または挿入する
async def upsert(userid, roleid, zirnum, isExcellent):
    now = get_current_datetime()
    
    # 既存レコードを取得
    record = await get_user_single(userid, roleid)
    
    if record:
        # 既存レコードを更新
        data = {
            "zirnum": record[3] + zirnum,
            "m_cnt": record[4] + 1,
            "ex_cnt": record[5] + (1 if isExcellent else 0),
            "done_flag": 1,
            "updated_at": now
        }
        return await upsert_record(config.DB_MINING, "MINING", userid, data, roleid)
    else:
        # 新規レコードを作成
        data = {
            "zirnum": zirnum,
            "m_cnt": 1,
            "ex_cnt": 1 if isExcellent else 0,
            "done_flag": 1,
            "updated_at": now
        }
        return await upsert_record(config.DB_MINING, "MINING", userid, data, roleid)


# ユーザのランキングを取得する
async def get_rank_user_country(roleid):
    return await get_rank(config.DB_MINING, "MINING", "user_country", roleid)


# 国のランキングを取得する
async def get_country_ranks():
    try:
        with sqlite3.connect(config.DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT roleid, SUM(zirnum)
                FROM MINING
                GROUP BY roleid
                ORDER BY SUM(zirnum) DESC
                """
            )
            results = cursor.fetchall()
            
            # 国名と採掘量のリストを作成
            ranks = []
            for roleid, amount in results:
                country = util.get_country_by_roleid(roleid)
                if country:
                    ranks.append((country["name"], amount))
            return ranks
    except sqlite3.Error as e:
        handle_db_error(e, "GET_COUNTRY_RANKS", config.DB_MINING)
        return []


# 全ユーザーのイベント統計情報を取得する
async def get_all_event_stats(guild):
    try:
        with sqlite3.connect(config.DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT userid, roleid, zirnum, m_cnt, ex_cnt
                FROM MINING
                ORDER BY zirnum DESC
                """
            )
            results = cursor.fetchall()
            
            # 統計情報のリストを作成
            stats = []
            for userid, roleid, zirnum, m_cnt, ex_cnt in results:
                # 国情報を取得
                country = util.get_country_by_roleid(roleid)
                country_name = country["name"] if country else "不明"
                
                # ユーザー情報を取得
                user = guild.get_member(userid)
                username = user.display_name if user else "不明"
                mention = user.mention if user else f"<@{userid}>"
                
                stats.append({
                    "user_id": userid,
                    "username": username,
                    "mention": mention,
                    "country": country_name,
                    "zirnum": zirnum,
                    "m_cnt": m_cnt,
                    "ex_cnt": ex_cnt
                })
            return stats
    except sqlite3.Error as e:
        handle_db_error(e, "GET_ALL_EVENT_STATS", config.DB_MINING)
        return []


# データベースをリセットする
async def reset_db():
    return await reset_db_table(config.DB_MINING, "MINING")
