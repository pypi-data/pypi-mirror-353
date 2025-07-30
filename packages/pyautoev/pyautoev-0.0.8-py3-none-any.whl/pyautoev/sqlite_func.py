# -*- coding: utf-8 -*-
import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

def insert_(sqlite_path, df, table_name):
    # 定义常量字符串
    SUCCESS_MESSAGE = 'Data inserted successfully'
    EMPTY_DF_MESSAGE = "{} is empty"
    ERROR_MESSAGE = "Error inserting data: {}"
    INVALID_INPUT_MESSAGE = "Invalid input: {}"

    # 参数校验
    if sqlite_path is None or not isinstance(sqlite_path, str) or sqlite_path.strip() == "":
        return INVALID_INPUT_MESSAGE.format("sqlite_path is invalid")
    if table_name is None or not isinstance(table_name, str) or table_name.strip() == "":
        return INVALID_INPUT_MESSAGE.format("table_name is invalid")
    if df is None or not isinstance(df, pd.DataFrame):
        return INVALID_INPUT_MESSAGE.format("df is invalid")

    try:
        # 检查 DataFrame 是否为空
        if df.empty:
            return EMPTY_DF_MESSAGE.format(table_name)

        # 创建 SQLAlchemy 引擎
        engine = create_engine(f'sqlite:///{sqlite_path}', echo=False)  # 禁用调试输出

        # 动态调整 chunksize
        df_size = len(df)
        chunksize = max(1, df_size // 10)  # 将 chunksize 设置为 DataFrame 大小的 1/10，最小为 1

        # 使用 pandas 的 to_sql 方法插入数据
        with engine.begin() as connection:  # 确保资源正确释放
            df.to_sql(
                table_name,
                con=connection,
                if_exists='append',
                index=False,
                chunksize=chunksize,
                method='multi'
            )

        return SUCCESS_MESSAGE  # 插入成功

    except SQLAlchemyError as e:
        # 捕获 SQLAlchemy 特定异常
        return ERROR_MESSAGE.format("SQLAlchemy error occurred: " + str(e))
    except Exception as e:
        # 捕获其他未知异常
        return ERROR_MESSAGE.format("An unexpected error occurred: " + str(e))
    finally:
        # 确保引擎关闭
        if 'engine' in locals():
            engine.dispose()




def delete_(sqlite_path, table_name, condition=None):
    try:
        # 校验sqlite_path是否有效
        if not os.path.isfile(sqlite_path) and sqlite_path != ":memory:":
            return {"status": "error", "message": f"SQLite database file does not exist: {sqlite_path}"}

        # 创建SQLAlchemy引擎，仅在调试时启用echo
        engine = create_engine(f'sqlite:///{sqlite_path}', echo=False)

        with engine.connect() as connection:
            # 构建删除语句，防止SQL注入
            if condition:
                # 验证条件是否安全（假设condition为简单的键值对形式）
                if not isinstance(condition, str) or ";" in condition:
                    return {"status": "error", "message": "Invalid condition provided"}
                delete_statement = text(f"DELETE FROM {table_name} WHERE {condition}")
            else:
                delete_statement = text(f"DELETE FROM {table_name}")

            # 执行删除语句
            result = connection.execute(delete_statement)

        # 返回结构化结果
        return {"status": "success", "message": f"{result.rowcount} rows deleted successfully"}

    except FileNotFoundError:
        return {"status": "error", "message": f"Database file not found: {sqlite_path}"}
    except Exception as e:
        return {"status": "error", "message": f"Error deleting data: {e}"}
    finally:
        # 确保引擎关闭
        if 'engine' in locals():
            engine.dispose()
