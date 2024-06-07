import sqlite3
import datetime
from config import DB_MINING

# 採掘結果のテーブル作成
async def create_zmdb():
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS MINING(
                           id INTEGER primary key autoincrement,
                           userid INTEGER,
                           roleid INTEGER,
                           zirnum INTEGER,
                           updated_at TIMESTAMP
                        )
            """)
    except sqlite3.Error as e:
        print('DB CREATION ERROR: ', e)
    finally:
        connection.close()

# テーブルの中身をすべてクリア
async def reset_zmdb():
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                        DELETE
                        FROM MINING
            """)
    except sqlite3.Error as e:
        print('DB CREATION ERROR: ', e)
    finally:
        connection.close()

# ユーザーごとの結果を返却する
async def get_user_result(userid, roleid):
    result = None
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT userid, roleid, zirnum, updated_at
                FROM MINING 
                WHERE userid = ?
                AND roleid = ?
            """,
            (userid, roleid))
            result = cursor.fetchone()
    except sqlite3.Error as e:
        print('DB ERROR: ', e)
    finally:
        connection.close()
    # [0]=userid, [1]=roleid, [2]=zirnum, [3]=updated timestamp(UNIX)
    return result

# 国ごとの合計をすべて取得
async def select_total_all_country():
    result = None
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT roleid, TOTAL(zirnum)
                FROM MINING 
                GROUP BY roleid
            """)
            result = cursor.fetchall()
    except sqlite3.Error as e:
        print('DB ERROR: ', e)
    finally:
        connection.close()
    # List of result, [0]=roleid, [1]=total of zirnum
    return result

# 指定された国の合計を取得
async def select_total_single_country(roleid):
    result = None
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT roleid, TOTAL(zirnum)
                FROM MINING
                WHERE roleid = ?
            """,
            (roleid,))
            result = cursor.fetchone()
    except sqlite3.Error as e:
        print('DB ERROR: ', e)
    finally:
        connection.close()
    # [0]=roleid, [1]=total of zirnum
    return result

# 採掘結果をUPSERT
async def insert_mining(userid, roleid, zirnum):
    timestamp = datetime.datetime.now().timestamp()
    try:
        with sqlite3.connect(DB_MINING) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM MINING WHERE userid = ? AND roleid = ?
            """, (userid, roleid))
            exst_record = cursor.fetchone()

            print(exst_record, zirnum)
            if exst_record:
                # レコードが存在する場合はzirnumをUPDATE
                updated_zirnum = exst_record[3] + zirnum
                print(updated_zirnum)
                cursor.execute("""
                UPDATE MINING SET
                    zirnum = ?,
                    updated_at = ?
                WHERE
                    userid = ?
                    AND roleid = ?
                """,
                (updated_zirnum, timestamp, userid, roleid))
            else:
                # レコードが存在しない場合はINSERT
                cursor.execute("""
                    INSERT INTO MINING
                        (userid, roleid, zirnum, updated_at)
                        VALUES(?, ?, ?, ?)
                """,
                (userid, roleid, zirnum, timestamp))
    except sqlite3.Error as e:
        print('DB ERROR: ', e)
    finally:
        connection.close()