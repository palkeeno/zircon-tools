import datetime
import sqlite3
import traceback
from typing import List, Tuple, Any, Optional, Callable, Dict, Union

from consts.const import JST, LONG_DT_FORMAT
from config import DB_MINING, DB_USERS
from consts.sysmsg import ERROR_MESSAGES


# エラーハンドリング関数
def handle_db_error(error: sqlite3.Error, operation: str, db_path: str) -> None:
    """データベース操作のエラーを処理する関数

    Args:
        error (sqlite3.Error): 発生したエラー
        operation (str): 実行していた操作の名前
        db_path (str): データベースのパス
    """
    error_time = datetime.datetime.now(JST).strftime(LONG_DT_FORMAT)
    error_type = type(error).__name__
    error_msg = str(error)
    stack_trace = traceback.format_exc()
    
    error_log = f"""
データベースエラーが発生しました
時間: {error_time}
データベース: {db_path}
操作: {operation}
エラータイプ: {error_type}
エラーメッセージ: {error_msg}
スタックトレース:
{stack_trace}
"""
    print(error_log)
    
    # エラーの種類に応じて適切なメッセージを返す
    if isinstance(error, sqlite3.IntegrityError):
        return ERROR_MESSAGES['DB_ERROR']
    elif isinstance(error, sqlite3.OperationalError):
        return ERROR_MESSAGES['DB_ERROR']
    else:
        return ERROR_MESSAGES['SYSTEM_ERROR']


# データベース接続を取得する
def get_connection(db_path: str) -> sqlite3.Connection:
    """データベース接続を取得する関数

    Args:
        db_path (str): データベースのパス

    Returns:
        sqlite3.Connection: データベース接続
    """
    return sqlite3.connect(db_path)


# データベースが新規かどうかを判定する
def is_new_db(connection: sqlite3.Connection, table_name: str) -> bool:
    """データベースが新規かどうかを判定する関数

    Args:
        connection (sqlite3.Connection): データベース接続
        table_name (str): テーブル名

    Returns:
        bool: 新規の場合はTrue、そうでない場合はFalse
    """
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE userid = 1")
    return cursor.fetchone() is None


# テーブルを作成する
def create_table(connection: sqlite3.Connection, table_name: str, schema: str) -> None:
    """テーブルを作成する関数

    Args:
        connection (sqlite3.Connection): データベース接続
        table_name (str): テーブル名
        schema (str): テーブルのスキーマ
    """
    cursor = connection.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name}{schema}")


# データベースを初期化する
async def init_db(
    db_path: str, table_name: str, schema: str, init_func: Optional[Callable] = None
) -> bool:
    """データベースを初期化する関数

    Args:
        db_path (str): データベースのパス
        table_name (str): テーブル名
        schema (str): テーブルのスキーマ
        init_func (Optional[Callable], optional): 初期化関数. Defaults to None.

    Returns:
        bool: 新規作成の場合はTrue、そうでない場合はFalse
    """
    is_new = False
    try:
        connection = get_connection(db_path)
        create_table(connection, table_name, schema)
        is_new = is_new_db(connection, table_name)
        if is_new and init_func:
            init_func()
    except sqlite3.Error as e:
        handle_db_error(e, "INIT", db_path)
    finally:
        connection.close()
    return is_new


# 現在の日時を取得する
def get_current_datetime() -> str:
    """現在の日時を取得する関数

    Returns:
        str: 現在の日時（文字列）
    """
    return datetime.datetime.now(JST).strftime(LONG_DT_FORMAT)


# 単一レコードを取得する
async def get_single_record(
    db_path: str, table_name: str, userid: int, roleid: Optional[int] = None
) -> Optional[Tuple]:
    """単一レコードを取得する関数

    Args:
        db_path (str): データベースのパス
        table_name (str): テーブル名
        userid (int): ユーザーID
        roleid (Optional[int], optional): ロールID. Defaults to None.

    Returns:
        Optional[Tuple]: 取得したレコード、存在しない場合はNone
    """
    result = None
    try:
        connection = get_connection(db_path)
        cursor = connection.cursor()
        if roleid is not None:
            cursor.execute(
                f"""
                SELECT *
                FROM {table_name}
                WHERE userid = ? AND roleid = ?
                """,
                (userid, roleid),
            )
        else:
            cursor.execute(
                f"""
                SELECT *
                FROM {table_name}
                WHERE userid = ?
                """,
                (userid,),
            )
        result = cursor.fetchone()
    except sqlite3.Error as e:
        handle_db_error(e, "GET_SINGLE", db_path)
    finally:
        connection.close()
    return result


# レコードを更新または挿入する
async def upsert_record(
    db_path: str, table_name: str, userid: int, data: Dict, roleid: Optional[int] = None
) -> None:
    """レコードを更新または挿入する関数

    Args:
        db_path (str): データベースのパス
        table_name (str): テーブル名
        userid (int): ユーザーID
        data (Dict): 更新または挿入するデータ
        roleid (Optional[int], optional): ロールID. Defaults to None.
    """
    try:
        connection = get_connection(db_path)
        cursor = connection.cursor()
        if roleid is not None:
            cursor.execute(
                f"""
                SELECT *
                FROM {table_name}
                WHERE userid = ? AND roleid = ?
                """,
                (userid, roleid),
            )
        else:
            cursor.execute(
                f"""
                SELECT *
                FROM {table_name}
                WHERE userid = ?
                """,
                (userid,),
            )
        existing_record = cursor.fetchone()

        if existing_record:
            # レコードが存在する場合は更新
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values())
            if roleid is not None:
                values.extend([userid, roleid])
                where_clause = "userid = ? AND roleid = ?"
            else:
                values.append(userid)
                where_clause = "userid = ?"
            cursor.execute(
                f"""
                UPDATE {table_name}
                SET {set_clause}
                WHERE {where_clause}
                """,
                values,
            )
        else:
            # レコードが存在しない場合は挿入
            columns = ["userid"] + list(data.keys())
            if roleid is not None:
                columns.append("roleid")
            placeholders = ", ".join(["?" for _ in columns])
            values = [userid] + list(data.values())
            if roleid is not None:
                values.append(roleid)
            cursor.execute(
                f"""
                INSERT INTO {table_name}
                ({", ".join(columns)})
                VALUES({placeholders})
                """,
                values,
            )
        connection.commit()
    except sqlite3.Error as e:
        handle_db_error(e, "UPSERT", db_path)
    finally:
        connection.close()


# データベースをリセットする
async def reset_db(db_path: str, table_name: str) -> None:
    """データベースをリセットする関数

    Args:
        db_path (str): データベースのパス
        table_name (str): テーブル名
    """
    try:
        connection = get_connection(db_path)
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        connection.commit()
    except sqlite3.Error as e:
        handle_db_error(e, "RESET", db_path)
    finally:
        connection.close()


# ランキングを取得する
async def get_rank(
    db_path: str, table_name: str, rank_type: str, roleid: Optional[int] = None
) -> List[List[Union[int, str]]]:
    """ランキングを取得する関数

    Args:
        db_path (str): データベースのパス
        table_name (str): テーブル名
        rank_type (str): ランキングの種類（"current"または"lifetime"）
        roleid (Optional[int], optional): ロールID. Defaults to None.

    Returns:
        List[List[Union[int, str]]]: ランキングデータ
    """
    result = None
    try:
        connection = get_connection(db_path)
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
        
        result = cursor.fetchall()
    except sqlite3.Error as e:
        handle_db_error(e, "GET_RANK", db_path)
    finally:
        connection.close()

    # ランキングデータを整形
    result_list = [[0] * 6 for i in range(len(result))]
    for index, res in enumerate(result):
        result_list[index][0] = int(index + 1)  # rank
        result_list[index][1] = res[0]  # userid
        result_list[index][2] = ""  # ユーザmentionの予約地
        result_list[index][3] = int(res[1])  # current/lifetime total
        result_list[index][4] = int(res[2])  # mining count
        result_list[index][5] = int(res[3])  # excellent count
    return result_list 