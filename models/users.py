import datetime
import sqlite3

import util
from config import COUNTRIES, DB_USERS
from consts.const import CURRENT, JST, LIFETIME, LONG_DT_FORMAT


# 国を無視した個人の採掘累計のテーブル作成
### current_total: 現在のzirnum合計（消費する可能性を考慮）
### lifetime_total: 生涯の合計zirnum（消費してもここからは減らさない）
### m_cnt, ex_cnt: 生涯の採掘回数合計、EX回数合計（消費しないのでlt）
async def create_db():
    isNew = False
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            # ユーザテーブルがなければ作成
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS USERS(
                    id INTEGER primary key autoincrement,
                    userid INTEGER,
                    curr_total INTEGER,
                    lt_total INTEGER,
                    m_cnt INTEGER,
                    ex_cnt INTEGER,
                    updated_at TEXT
                )
            """
            )
            # 新規作成かどうか判定
            cursor.execute(
                """
                SELECT * FROM USERS WHERE userid = 1
            """
            )
            isNew = cursor.fetchone() is None
    except sqlite3.Error as e:
        print("DB-USERS CREATION ERROR: ", e)
    finally:
        connection.close()

    # データベースを新規作成する場合、国ユーザを初期作成
    if isNew:
        init_country_record()


# 国ユーザを初期で作成する
def init_country_record():
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            now = util.convertDt2Str(datetime.datetime.now(JST), LONG_DT_FORMAT)
            for country in COUNTRIES:
                cursor.execute(
                    """
                    INSERT INTO USERS
                        (userid, curr_total, lt_total, m_cnt, ex_cnt, updated_at)
                        VALUES(?, 0, 0, 0, 0, ?)
                """,
                    (country["id"], now),
                )
    except sqlite3.Error as e:
        print("DB-USERS INITIALIZE ERROR: ", e)
    finally:
        connection.close()


# ユーザテーブルの中身をすべてクリア
async def reset_db():
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                DELETE
                FROM USERS
            """
            )
    except sqlite3.Error as e:
        print("DB-USERS RESET ERROR: ", e)
    finally:
        connection.close()


# ユーザテーブルの１つのレコードを削除
async def delete_single(userid):
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                DELETE
                FROM USERS
                WHERE userid = ?
            """,
                (userid),
            )
    except sqlite3.Error as e:
        print("DB-USERS DELETE ERROR: ", e)
    finally:
        connection.close()


# ユーザーごとの結果を返却する
async def get_single(userid):
    result = None
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT userid, curr_total, lt_total, m_cnt, ex_cnt
                FROM USERS
                WHERE userid = ?
            """,
                (userid,),
            )
            result = cursor.fetchone()
    except sqlite3.Error as e:
        print("DB-USERS GET_SINGLE ERROR: ", e)
    finally:
        connection.close()
    # [0]=userid, [1]=current total, [2]=lifetime total, [3]=m_cnt, [4]=ex_cnt
    return result


# 全ユーザの現在／生涯蓄積数ランキングをすべて取得する
async def get_rank(args):
    result = None
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            # currentなら現在蓄積数ランク
            if args == CURRENT:
                cursor.execute(
                    """
                    SELECT userid, curr_total, m_cnt, ex_cnt
                    FROM USERS
                    WHERE userid not in (1,2,3,4)
                    ORDER BY curr_total DESC
                """
                )
            # lifetimeなら生涯蓄積数ランク
            elif args == LIFETIME:
                cursor.execute(
                    """
                    SELECT userid, lt_total, m_cnt, ex_cnt
                    FROM USERS
                    WHERE userid not in (1,2,3,4)
                    ORDER BY lt_total DESC
                """
                )
            result = cursor.fetchall()
    except sqlite3.Error as e:
        print("DB GET_RANK ERROR: ", e)
    finally:
        connection.close()
    # [N][0]=userid, [N][1]=current/lifetime total, [N][2]=m_cnt, [N][3]=ex_cnt
    result_list = [[0] * 6 for i in range(len(result))]
    for index, res in enumerate(result):
        result_list[index][0] = int(index + 1)  # rank
        result_list[index][1] = res[0]  # userid
        result_list[index][2] = ""  # ユーザmentionの予約地
        result_list[index][3] = int(res[1])  # current/lifetime total
        result_list[index][4] = int(res[2])  # mining count
        result_list[index][5] = int(res[3])  # excellent count
    return result_list


# 採掘結果をUPSERT(運営addの場合はisMining=False)
async def upsert(userid, zirnum, isExcellent=False, isMining=True):
    dt = util.convertDt2Str(datetime.datetime.now(JST), LONG_DT_FORMAT)
    # ユーザテーブルにUPSERT
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT * FROM USERS WHERE userid = ?
            """,
                (userid,),
            )
            exst_record = cursor.fetchone()

            if exst_record:
                print("test1")
                # レコードが存在する場合はをUPDATE
                updated_curr = exst_record[2] + zirnum
                updated_lt = exst_record[3] + (zirnum if zirnum > 0 else 0)
                updated_cnt = exst_record[4] + isMining
                updated_ex = exst_record[5] + isExcellent
                cursor.execute(
                    """
                UPDATE USERS SET
                    curr_total = ?,
                    lt_total = ?,
                    m_cnt = ?,
                    ex_cnt = ?,
                    updated_at = ?
                WHERE
                    userid = ?
                """,
                    (updated_curr, updated_lt, updated_cnt, updated_ex, dt, userid),
                )
            else:
                print("test2")
                # レコードが存在しない場合はINSERT
                cursor.execute(
                    """
                    INSERT INTO USERS
                        (userid, curr_total, lt_total, m_cnt, ex_cnt, updated_at)
                        VALUES(?, ?, ?, 1, ?, ?)
                """,
                    (userid, zirnum, zirnum, isExcellent, dt),
                )
    except sqlite3.Error as e:
        print("DB-USERS UPSERT ERROR: ", e)
        print("userid: ", userid)
    finally:
        connection.close()
