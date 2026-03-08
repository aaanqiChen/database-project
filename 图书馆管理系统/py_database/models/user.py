from database.connection import get_db_connection

class User:
    @staticmethod
    def add_user(username, password, contact):
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    insert_sql = """
                                 INSERT INTO user(user_name, password, phone)
                                 VALUES (%s, %s, %s)
                                 """
                    cursor.execute(insert_sql, (username, password, contact))
                connection.commit()
                return True  # 返回成功状态
        except Exception as e:
            print(f"Error adding user: {e}")
            return False  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()

    @staticmethod
    def is_user_in(username):
        user = None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    query_user_sql = """
                                     SELECT *
                                     FROM user
                                     WHERE user_name = %s \
                                     """
                    cursor.execute(query_user_sql, (username,))
                    user = cursor.fetchone()
                connection.commit()
                if user is not None:
                    return True  # 返回成功状态
        except Exception as e:
            print(f"Error adding user: {e}")
            return False  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()

    @staticmethod
    def is_user_pw(username, password):
        user_pw= None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    query_user_sql = """
                                     SELECT password
                                     FROM user
                                     WHERE user_name = %s \
                                     """
                    cursor.execute(query_user_sql, (username,))
                    user_pw= cursor.fetchone()
                    print(user_pw)
                connection.commit()
                if(password == user_pw['password']):
                    return True  # 返回成功状态
        except Exception as e:
            print(f"Error adding user: {e}")
            return False  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()

    @staticmethod
    def query_muser_data(username):
        user_data= None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    query_user_data_sql = """
                                          SELECT u.user_name, m.access_level, m.management_scope, m.department
                                          FROM user u
                                                   JOIN manager m ON u.user_id = m.user_id
                                          WHERE u.user_name = %s \
                                          """
                    cursor.execute(query_user_data_sql, (username,))
                    user_data= cursor.fetchone()
                connection.commit()
                if(user_data is not None):
                    return user_data # 返回成功状态
        except Exception as e:
            print(f"Error querying user data: {e}")
            return None  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()

    @staticmethod
    def query_user_data(username):
        user_data = None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    # 密码正确，获取用户详细信息
                    query_user_data_sql = """
                                          SELECT u.user_id,u.user_name, r.brief_intro, r.can_borrow_num, r.credit_level
                                          FROM user u
                                                   JOIN reader r ON u.user_id = r.user_id
                                          WHERE u.user_name = %s \
                                          """
                    cursor.execute(query_user_data_sql, (username,))
                    user_data = cursor.fetchone()
                connection.commit()
                if (user_data is not None):
                    return user_data  # 返回成功状态
        except Exception as e:
            print(f"Error querying user data: {e}")
            return None  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()

    @staticmethod
    def is_user_delete(user_id):
        connection = None
        try:
            connection = get_db_connection()
            if connection:
                print(f"数据库连接已建立: {connection}")  # 调试信息：数据库连接

                # 开启事务
                with connection.cursor() as cursor:
                    print("事务已开启")  # 调试信息：事务开启

                    cursor.execute('START TRANSACTION')  # 使用游标执行SQL
                    # 检查用户是否存在
                    query_user_sql = """
                                     SELECT user_id
                                     FROM user
                                     WHERE user_id = %s \
                                     """
                    print(f"执行查询用户SQL: {query_user_sql}，参数: {user_id}")  # 调试信息：查询用户
                    cursor.execute(query_user_sql, (user_id,))
                    user_exists = cursor.fetchone()
                    print(f"查询结果: {user_exists}")  # 调试信息：查询结果

                    if not user_exists:
                        print("用户不存在")  # 调试信息：用户不存在
                        connection.rollback()  # 回滚事务
                        return 1

                    # 检查用户是否存在未还书籍
                    query_user_sql2 = """
                                     SELECT *
                                     FROM borrow_record
                                     WHERE user_id = %s AND state='借出'
                                     """
                    print(f"执行查询用户SQL: {query_user_sql2}，参数: {user_id}")  # 调试信息：查询用户
                    cursor.execute(query_user_sql2, (user_id,))
                    have_book = cursor.fetchone()
                    print(f"查询结果: {have_book}")  # 调试信息：查询结果


                    if have_book is not None:
                        print("用户存在未还书籍")  # 调试信息：用户不存在
                        connection.rollback()  # 回滚事务
                        return 2

                    delete_fine_record_sql = """
                                             DELETE \
                                             FROM fine_record
                                             WHERE borrow_id IN (SELECT borrow_id \
                                                                 FROM borrow_record \
                                                                 WHERE user_id = %s) \
                                             """
                    print(f"执行删除罚款记录SQL: {delete_fine_record_sql}，参数: {user_id}")  # 调试信息：删除罚款记录
                    cursor.execute(delete_fine_record_sql, (user_id,))

                    # 删除用户的借阅记录
                    print("执行删除借阅记录")  # 调试信息：删除借阅记录
                    cursor.execute('DELETE FROM borrow_record WHERE user_id = %s', (user_id,))

                    # 删除用户信息
                    print("执行删除用户信息")  # 调试信息：删除用户信息
                    cursor.execute('DELETE FROM user WHERE user_id = %s', (user_id,))

                    cursor.execute('DELETE FROM reader WHERE user_id = %s', (user_id,))

                    # 提交事务
                    print("提交事务")  # 调试信息：提交事务
                    connection.commit()
                    return 3  # 返回成功状态

        except Exception as e:
            print(f"删除用户时发生错误: {e}")  # 调试信息：错误信息
            if connection:
                connection.rollback()  # 回滚事务
            return 4  # 返回失败状态
        finally:
            if connection:
                connection.close()  # 确保连接关闭
                print("数据库连接已关闭")  # 调试信息：连接关闭

    def update_user_bio_in_database(user_id, bio):
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE reader SET brief_intro = %s WHERE user_id = %s", (bio, user_id))
                connection.commit()
        except Exception as e:
            print(f"数据库错误: {e}")
            connection.rollback()
        finally:
            if connection and connection.open:
                connection.close()

    @staticmethod
    def query_noborrow_user():
        user_data = None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    query_user_data_sql = """
                                          SELECT user.user_name,user.user_id
                                          FROM user
                                          WHERE not EXISTS(SELECT *
                                                           FROM borrow_record 
                                                           WHERE borrow_record.user_id =user.user_id AND borrow_record.state='借出'
                                                           )  
                                          ORDER BY user_id
                                          """
                    cursor.execute(query_user_data_sql)
                    user_data = cursor.fetchall()
                connection.commit()
                if (user_data is not None):
                    return user_data  # 返回成功状态
        except Exception as e:
            print(f"Error querying user data: {e}")
            return None  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()

    @staticmethod
    def get_all_users():
        user_data = None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    query_user_data_sql = """
                                          SELECT user.user_name, user.user_id
                                          FROM user
                                          ORDER BY user_id
                                          """
                    cursor.execute(query_user_data_sql)
                    user_data = cursor.fetchall()
                connection.commit()
                if (user_data is not None):
                    return user_data  # 返回成功状态
        except Exception as e:
            print(f"Error querying user data: {e}")
            return None  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()

