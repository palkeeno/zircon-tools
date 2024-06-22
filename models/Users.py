import sqlite3
import datetime
from config import DB_USERS
from config import COUNTRIES
from consts.constants import JST
from consts.constants import LONG_DT_FORMAT
import util

# 国を無視した個人の採掘累計のテーブル作成
### lt_totalは今後のための構え
async def create_db():
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            # ユーザテーブルがなければ作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS USERS(
                    id INTEGER primary key autoincrement,
                    userid INTEGER,
                    zirnum INTEGER,
                    lt_total INTEGER,
                    m_cnt INTEGER,
                    ex_cnt INTEGER,
                    updated_at TEXT
                )
            """)
    except sqlite3.Error as e:
        print('DB-USERS CREATION ERROR: ', e)
    finally:
        connection.close() 

# ユーザテーブルの中身をすべてクリア
async def reset_db():
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                DELETE
                FROM USERS
            """)
    except sqlite3.Error as e:
        print('DB-USERS RESET ERROR: ', e)
    finally:
        connection.close()

# ユーザテーブルの１つのレコードを削除
async def delete_single(userid):
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                DELETE
                FROM USERS
                WHERE userid = ?
            """,
            (userid))
    except sqlite3.Error as e:
        print('DB-USERS DELETE ERROR: ', e)
    finally:
        connection.close()

# ユーザーごとの結果を返却する
async def get_single(userid):
    result = None
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT userid, zirnum, lt_total, m_cnt, ex_cnt
                FROM USERS
                WHERE userid = ?
            """,
            (userid))
            result = cursor.fetchone()
    except sqlite3.Error as e:
        print('DB-USERS GET_SINGLE ERROR: ', e)
    finally:
        connection.close()
    # [0]=userid, [1]=zirnum, [2]=lifetime total, [3]=m_cnt, [4]=ex_cnt
    return result

# 全ユーザの現在の蓄積数ランキングをすべて取得する
async def get_rank_current():
    result = None
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT userid, zirnum, m_cnt, ex_cnt
                FROM USERS
                ORDER BY zirnum DESC
            """)
            result = cursor.fetchall()
    except sqlite3.Error as e:
        print('DB GET_RANK_CURRENT ERROR: ', e)
    finally:
        connection.close()
    # [N][0]=userid, [N][1]=zirnum, [N][2]=m_cnt, [N][3]=ex_cnt order by zirunm
    result_list = [[0]*6 for i in range(len(result))]
    for index, res in enumerate(result):
        result_list[index][0] = int(index + 1) # rank
        result_list[index][1] = res[0] # userid
        result_list[index][2] = int(res[1]) # zirnum
        result_list[index][3] = int(res[2]) # mining count
        result_list[index][4] = int(res[3]) # excellent count
        result_list[index][5] = "" # ユーザmentionの予約地
    return result_list

# 全ユーザの生涯の蓄積数ランキングをすべて取得する
async def get_rank_lifetime():
    result = None
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT userid, lt_total, m_cnt, ex_cnt
                FROM USERS
                ORDER BY lt_total DESC
            """)
            result = cursor.fetchall()
    except sqlite3.Error as e:
        print('DB GET_RANK_LIFETIME ERROR: ', e)
    finally:
        connection.close()
    # [N][0]=userid, [N][1]=lt_total, [N][2]=m_cnt, [N][3]=ex_cnt order by zirunm
    result_list = [[0]*7 for i in range(len(result))]
    for index, res in enumerate(result):
        result_list[index][0] = int(index + 1) # rank
        result_list[index][1] = res[0] # userid
        result_list[index][2] = int(res[1]) # lifetime total zirnum
        result_list[index][3] = int(res[2]) # mining count
        result_list[index][4] = int(res[3]) # excellent count
        result_list[index][5] = "" # ユーザmentionの予約地
    return result_list
    
# 採掘結果をUPSERT
# TODO: add_flag を追加してaddの時はupsert項目を変えるように修正（優先度：低）
async def upsert(userid, zirnum, isExcellent):
    dt = util.convertDt2Str(datetime.datetime.now(JST), LONG_DT_FORMAT)
    # ユーザテーブルにUPSERT
    try:
        with sqlite3.connect(DB_USERS) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM USERS WHERE userid = ?
            """, (userid))
            exst_record = cursor.fetchone()
            
            if exst_record:
                # レコードが存在する場合はをUPDATE
                updated_zirnum = exst_record[3] + zirnum
                updated_cnt = exst_record[4] + 1
                updated_ex = exst_record[5] + isExcellent
                cursor.execute("""
                UPDATE USERS SET
                    zirnum = ?,
                    m_cnt = ?,
                    ex_cnt = ?,
                    updated_at = ?
                WHERE
                    userid = ?
                """,
                (updated_zirnum, updated_cnt, updated_ex, dt, userid))
            else:
                # レコードが存在しない場合はINSERT
                cursor.execute("""
                    INSERT INTO USERS
                        (userid, zirnum, m_cnt, ex_cnt, updated_at)
                        VALUES(?, ?, 1, ?, ?)
                """,
                (userid, zirnum, isExcellent, dt))
    except sqlite3.Error as e:
        print('DB-USERS UPSERT ERROR: ', e)
    finally:
        connection.close()
