import datetime
import sqlite3
from typing import List, Tuple, Any, Optional, Callable

from consts.const import JST, LONG_DT_FORMAT


# データベース接続を取得する
def get_connection(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


# データベースが新規作成かどうかを判定する
def is_new_db(connection: sqlite3.Connection, table_name: str) -> bool:
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE userid = 1")
    return cursor.fetchone() is None


# テーブルを作成する
def create_table(connection: sqlite3.Connection, table_name: str, schema: str) -> None:
    cursor = connection.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} {schema}")


# データベースを初期化する
async def init_db(db_path: str, table_name: str, schema: str, init_func: Optional[Callable] = None) -> bool:
    is_new = False
    try:
        with get_connection(db_path) as connection:
            create_table(connection, table_name, schema)
            is_new = is_new_db(connection, table_name)
    except sqlite3.Error as e:
        print(f"DB-{table_name} CREATION ERROR: {e}")
        return False

    # データベースを新規作成する場合、初期化関数を実行
    if is_new and init_func:
        init_func()
    
    return True


# 現在の日時を文字列で取得する
def get_current_datetime() -> str:
    return datetime.datetime.now(JST).strftime(LONG_DT_FORMAT)


# 単一レコードを取得する
async def get_single_record(db_path: str, table_name: str, userid: int, roleid: Optional[int] = None) -> Optional[Tuple]:
    try:
        with get_connection(db_path) as connection:
            cursor = connection.cursor()
            if roleid is not None:
                cursor.execute(f"SELECT * FROM {table_name} WHERE userid = ? AND roleid = ?", (userid, roleid))
            else:
                cursor.execute(f"SELECT * FROM {table_name} WHERE userid = ?", (userid,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"DB-{table_name} GET ERROR: {e}")
        return None


# レコードを更新または挿入する
async def upsert_record(db_path: str, table_name: str, userid: int, data: dict, roleid: Optional[int] = None) -> bool:
    try:
        with get_connection(db_path) as connection:
            cursor = connection.cursor()
            
            # 既存レコードを確認
            if roleid is not None:
                cursor.execute(f"SELECT * FROM {table_name} WHERE userid = ? AND roleid = ?", (userid, roleid))
            else:
                cursor.execute(f"SELECT * FROM {table_name} WHERE userid = ?", (userid,))
            
            record = cursor.fetchone()
            
            if record:
                # 更新
                set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
                values = list(data.values())
                values.append(userid)
                if roleid is not None:
                    values.append(roleid)
                    cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE userid = ? AND roleid = ?", values)
                else:
                    cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE userid = ?", values)
            else:
                # 挿入
                columns = ["userid"] + list(data.keys())
                if roleid is not None:
                    columns.append("roleid")
                
                placeholders = ", ".join(["?" for _ in columns])
                values = [userid] + list(data.values())
                if roleid is not None:
                    values.append(roleid)
                
                cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", values)
            
            connection.commit()
            return True
    except sqlite3.Error as e:
        print(f"DB-{table_name} UPSERT ERROR: {e}")
        return False


# データベースをリセットする
async def reset_db(db_path: str, table_name: str) -> bool:
    try:
        with get_connection(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM {table_name}")
            connection.commit()
            return True
    except sqlite3.Error as e:
        print(f"DB-{table_name} RESET ERROR: {e}")
        return False


# ランキングを取得する
async def get_rank(db_path: str, table_name: str, rank_type: str, roleid: Optional[int] = None) -> List[Tuple]:
    try:
        with get_connection(db_path) as connection:
            cursor = connection.cursor()
            
            if rank_type == "user_country" and roleid is not None:
                # 国内ユーザランキング
                cursor.execute(f"""
                    SELECT ROW_NUMBER() OVER (ORDER BY zirnum DESC) as rank, userid, zirnum, roleid
                    FROM {table_name}
                    WHERE roleid = ?
                    ORDER BY zirnum DESC
                """, (roleid,))
            elif rank_type == "user_overall":
                # 全ユーザランキング
                cursor.execute(f"""
                    SELECT ROW_NUMBER() OVER (ORDER BY zirnum DESC) as rank, userid, zirnum, roleid
                    FROM {table_name}
                    ORDER BY zirnum DESC
                """)
            elif rank_type == "country":
                # 国ランキング
                cursor.execute(f"""
                    SELECT roleid, SUM(zirnum) as total_zirnum, COUNT(*) as total_count
                    FROM {table_name}
                    GROUP BY roleid
                    ORDER BY total_zirnum DESC
                """)
            elif rank_type == "lifetime":
                # 生涯ランキング
                cursor.execute(f"""
                    SELECT ROW_NUMBER() OVER (ORDER BY lt_total DESC) as rank, userid, lt_total, m_cnt, ex_cnt
                    FROM {table_name}
                    ORDER BY lt_total DESC
                """)
            
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"DB-{table_name} RANK ERROR: {e}")
        return [] 