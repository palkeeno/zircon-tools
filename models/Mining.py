import sqlite3
import datetime
from config import DB_MINING
from config import COUNTRIES
from consts.constants import JST
from consts.constants import LONG_DT_FORMAT
import util

# 採掘結果のテーブル作成
### zirnum = number of mined zircon
### m_cnt = total count of mining as this user
### ex_cnt = total count of excellent as this user
### done_flag = the flag of wheather this user have done mining or not, 0:Flase, 1:True
async def create_db():
    isNew = False
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            # 採掘テーブルがなければ作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS MINING(
                    id INTEGER primary key autoincrement,
                    userid INTEGER,
                    roleid INTEGER,
                    zirnum INTEGER,
                    m_cnt INTEGER,
                    ex_cnt INTEGER,
                    done_flag INTEGER,
                    updated_at TEXT
                )
            """)
            # 新規作成かどうか判定
            cursor.execute("""
                SELECT * FROM MINING WHERE userid = 1
            """)
            isNew = (cursor.fetchone() == None)
    except sqlite3.Error as e:
        print('DB-MINING CREATION ERROR: ', e)
    finally:
        connection.close()
    
    # データベースを新規作成する場合、国ユーザを初期作成
    if isNew:
        init_country_record()

# 国ユーザを初期で作成する
def init_country_record():
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            now = util.convertDt2Str(datetime.datetime.now(JST), LONG_DT_FORMAT)
            for country in COUNTRIES:
                cursor.execute("""
                    INSERT INTO MINING
                        (userid, roleid, zirnum, m_cnt, ex_cnt, done_flag, updated_at)
                        VALUES(?, ?, 0, 0, 0, 0, ?)
                """, (country['id'], country['role'], now))
    except sqlite3.Error as e:
        print('DB-MINING INITIALIZE ERROR: ', e)
    finally:
        connection.close()

# 採掘テーブルの中身をすべてクリア
async def reset_db():
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                DELETE
                FROM MINING
            """)
    except sqlite3.Error as e:
        print('DB-MINING RESET ERROR: ', e)
    finally:
        connection.close()
    # 国ユーザを初期作成
    init_country_record()

# 採掘テーブルの"done_flag"を下げる
async def undo_done_flag():
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE MINING
                SET done_flag = 0
            """)
    except sqlite3.Error as e:
        print('DB UNDO_DONE_FLAG ERROR: ', e)
    finally:
        connection.close()

# ユーザー１人の結果を返却する
async def get_user_single(userid, roleid):
    result = None
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT userid, roleid, zirnum, done_flag, m_cnt, ex_cnt
                FROM MINING 
                WHERE userid = ?
                AND roleid = ?
            """,
            (userid, roleid))
            result = cursor.fetchone()
    except sqlite3.Error as e:
        print('DB GET_USER_RESULT ERROR: ', e)
    finally:
        connection.close()
    # [0]=userid, [1]=roleid, [2]=zirnum, [3]=done_flag, [4]=m_cnt, [5]=ex_cnt
    return result

# 指定の国のユーザ採掘ランキングをすべて取得する
async def get_rank_user_country(roleid):
    result = None
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT userid, zirnum
                FROM MINING
                WHERE roleid = ? AND userid not in (1,2,3,4)
                ORDER BY zirnum DESC
            """, (roleid, ))
            result = cursor.fetchall()
    except sqlite3.Error as e:
        print('DB GET_USER_RANK_BY_ROLE ERROR: ', e)
    finally:
        connection.close()
    # [N][0]=userid, [N][1]=zirnum, order by zirunm
    result_list = [[0]*3 for i in range(len(result))]
    for index, res in enumerate(result):
        result_list[index][0] = int(index + 1) # rank
        result_list[index][1] = res[0] # userid
        result_list[index][2] = int(res[1]) # zirnum
    return result_list

# 全体のユーザ採掘ランキングをすべて取得する
async def get_rank_user_overall():
    result = None
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT userid, zirnum, roleid, m_cnt, ex_cnt
                FROM MINING
                WHERE userid not in (1,2,3,4)
                ORDER BY zirnum DESC
            """)
            result = cursor.fetchall()
    except sqlite3.Error as e:
        print('DB GET_USER_RANK_OVERALL ERROR: ', e)
    finally:
        connection.close()
    # [N][0]=userid, [N][1]=zirnum, [N][2]=roleid, [N][3]=m_cnt, [N][4]=ex_cnt order by zirunm
    result_list = [[0]*7 for i in range(len(result))]
    for index, res in enumerate(result):
        result_list[index][0] = int(index + 1) # rank
        result_list[index][1] = res[0] # userid
        result_list[index][2] = int(res[1]) # zirnum
        result_list[index][3] = res[2] # roleid
        result_list[index][4] = int(res[3]) # mining count
        result_list[index][5] = int(res[4]) # excellent count
        result_list[index][6] = "" # ユーザmentionの予約地
    return result_list

# 国ごとの合計をすべて取得
async def get_country_each():
    result = None
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT roleid, TOTAL(zirnum), TOTAL(m_cnt)
                FROM MINING 
                GROUP BY roleid
            """)
            result = cursor.fetchall()
    except sqlite3.Error as e:
        print('DB GET_TOTAL_ALL_COUNTRIES ERROR: ', e)
    finally:
        connection.close()
    # [N][0]=roleid, [N][1]=total of zirnum, [N][2]=total of mining count
    result_list = [[0]*3 for i in range(len(result))]
    for index, res in enumerate(result):
        result_list[index][0] = res[0] # roleid
        result_list[index][1] = int(res[1]) # zirnum
        result_list[index][2] = int(res[2]) # mining count
    return result_list

# 指定された国の合計を取得
async def get_country_single(roleid):
    result = None
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT roleid, TOTAL(zirnum), TOTAL(m_cnt)
                FROM MINING
                WHERE roleid = ?
            """,
            (roleid, ))
            result = cursor.fetchone()
    except sqlite3.Error as e:
        print('DB GET_TOTAL_SINGLE_COUTNRY ERROR: ', e)
    finally:
        connection.close()
    # [0]=roleid, [1]=total of zirnum, [2]=total of mining count
    return result

# 採掘結果をUPSERT
# TODO: add_flag を追加してaddの時はupsert項目を変えるように修正（優先度：低）
async def upsert(userid, roleid, zirnum, isExcellent):
    dt = util.convertDt2Str(datetime.datetime.now(JST), LONG_DT_FORMAT)
    # 採掘テーブルにUPSERT
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM MINING WHERE userid = ? AND roleid = ?
            """, (userid, roleid))
            exst_record = cursor.fetchone()
            
            if exst_record:
                # レコードが存在する場合はUPDATE
                updated_zirnum = exst_record[3] + zirnum
                updated_cnt = exst_record[4] + 1
                updated_ex = exst_record[5] + isExcellent
                cursor.execute("""
                UPDATE MINING SET
                    zirnum = ?,
                    m_cnt = ?,
                    ex_cnt = ?,
                    done_flag = 1,
                    updated_at = ?
                WHERE
                    userid = ?
                    AND roleid = ?
                """,
                (updated_zirnum, updated_cnt, updated_ex, dt, userid, roleid))
            else:
                # レコードが存在しない場合はINSERT
                cursor.execute("""
                    INSERT INTO MINING
                        (userid, roleid, zirnum, m_cnt, ex_cnt, done_flag, updated_at)
                        VALUES(?, ?, ?, 1, ?, 1, ?)
                """,
                (userid, roleid, zirnum, isExcellent, dt))
    except sqlite3.Error as e:
        print('DB-MINING UPSERT ERROR: ', e)
    finally:
        connection.close()

# 採掘とは別にジルコンを追加
async def add_zirnum(userid, roleid, zirnum):
    dt = util.convertDt2Str(datetime.datetime.now(JST), LONG_DT_FORMAT)
    try:
        with sqlite3.connect(DB_MINING) as conn1:
            cursor = conn1.cursor()
            cursor.execute("""
                SELECT * FROM MINING WHERE userid = ? AND roleid = ?
            """, (userid, roleid))
            exst_record = cursor.fetchone()
            # レコードが存在する場合はzirnumをUPDATE
            updated_zirnum = exst_record[3] + zirnum
            cursor.execute("""
            UPDATE MINING SET
                zirnum = ?,
                updated_at = ?
            WHERE
                userid = ?
                AND roleid = ?
            """,
            (updated_zirnum, dt, userid, roleid))
    except sqlite3.Error as e:
        print('DB-MINING UPSERT ERROR: ', e)
        print('userid: ', userid)
    finally:
        conn1.close()
    