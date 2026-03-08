import pymysql

from database.connection import get_db_connection

class Fine:
    @staticmethod
    def get_all_fines(user_id):
        fine_data = None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    query_user_data_sql = """
                                          SELECT f.borrow_id,f.fine_amount,f.state
                                          FROM fine_record f NATURAL JOIN borrow_record b
                                          WHERE user_id = %s
                                          """
                    cursor.execute(query_user_data_sql, (user_id,))
                    fine_data = cursor.fetchall()
                connection.commit()
                if (fine_data is not None):
                    return fine_data  # 返回成功状态
        except Exception as e:
            print(f"Error querying user data: {e}")
            return None  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()
