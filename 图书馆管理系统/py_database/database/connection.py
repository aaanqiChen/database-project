import pymysql
from pymysql import cursors

# 数据库连接配置
db_config = {
    'host': 'localhost',  # 数据库服务器地址
    'user': 'root',  # 数据库用户名
    'password': 'c23456qroot',  # 数据库密码
    'database': 'aqlibrary',  # 数据库名称
    'charset': 'utf8mb4',  # 字符集
    'cursorclass': pymysql.cursors.DictCursor  # 返回字典类型的游标
}


def get_db_connection():
    try:
        connection = pymysql.connect(**db_config)
        print("Successfully connected to the database!")
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        return None
