import pymysql

from database.connection import get_db_connection

class Book:
    @staticmethod
    def add_book(book_name,writer_name,publisher,publish_date,price,bookcase_id,language,total_amount,brief_intro,catagory):
        connection = get_db_connection()
        cursor = connection.cursor()
        query_user_sql = """
                         SELECT writer_id
                         FROM writer
                         WHERE name = %s \
                         """
        cursor.execute(query_user_sql, (writer_name,))
        writer_re= cursor.fetchone()
        writer_id=writer_re['writer_id']
        stock=total_amount
        borrow_hot=0

        cursor.execute('INSERT INTO book (book_name,writer_id,publisher,publish_date,price,stock,borrow_hot,bookcase_id,language,total_amount,brief_intro,category_id) VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s)',
                       (book_name,writer_id,publisher,publish_date,price,stock,borrow_hot,bookcase_id,language,total_amount,brief_intro,catagory))

        connection.commit()
        connection.close()

    @staticmethod
    def query_nabook2(book_name):
        query_re = None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    query = f"SELECT category_id,book_id FROM book WHERE book_name = %s"
                    cursor.execute(query, (book_name,))
                    cateid= cursor.fetchall()
                    category_id = cateid['category_id']
                    book_id = cateid['book_id']

                    cursor.execute("SELECT cate_table FROM category WHERE category_id = %s", (category_id,))
                    cate_table = cursor.fetchone()['cate_table']

                    # 动态构建查询语句
                    query = f"SELECT * FROM {cate_table} WHERE book_id = %s"
                    cursor.execute(query, (book_id,))
                    query_re = cursor.fetchall()
                connection.commit()
                if (query_re is not None):
                    return query_re  # 返回成功状态
        except Exception as e:
            print(f"Error querying user data: {e}")
            return None  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()

    @staticmethod
    def query_nabook1(book_name):
        query_re = None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM book_with_category WHERE book_name = %s"
                    cursor.execute(sql, (book_name,))

                    query_re = cursor.fetchall()
                connection.commit()
                if (query_re is not None):
                    return query_re  # 返回成功状态
        except Exception as e:
            print(f"Error querying user data: {e}")
            return None  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()

    @staticmethod
    def query_wrbook1(author_name):
        query_re = None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM book_with_category WHERE name = %s"
                    cursor.execute(sql, (author_name,))

                    query_re = cursor.fetchall()
                connection.commit()
                if (query_re is not None):
                    return query_re  # 返回成功状态
        except Exception as e:
            print(f"Error querying user data: {e}")
            return None  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()


    @staticmethod
    def borrow_book(book_id, user_id):
        connection = None
        try:
            print(f"Attempting to borrow book with book_id={book_id} and user_id={user_id}")
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                                   INSERT INTO borrow_record (user_id, book_id, borrow_date, due_date, state)
                                   VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY), '借出')
                                   """, (user_id, book_id))
                connection.commit()
        except pymysql.Error as e:
            raise Exception(f'借阅失败：{e}')
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_fine_records(user_id):
        query_re = None  # 初始化 user 变量
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM book_with_fine WHERE user_id = %s"
                    cursor.execute(sql, (user_id,))

                    query_re = cursor.fetchall()
                connection.commit()
                if (query_re is not None):
                    return query_re  # 返回成功状态
        except Exception as e:
            print(f"Error querying user data: {e}")
            return None  # 返回失败状态
        finally:
            if connection and connection.open:
                connection.close()


    @staticmethod
    def get_borrow_records(user_id) :
        query_re = None
        connection = None
        try:
            connection = get_db_connection()
            if connection:
                with connection.cursor() as cursor:
                    # 检查用户是否存在
                    query_user_sql = """
                                     SELECT user_id
                                     FROM user
                                     WHERE user_id = %s \
                                     """
                    cursor.execute(query_user_sql, (user_id,))
                    user_exists = cursor.fetchone()
                    print(f"查询结果: {user_exists}")  # 调试信息：查询结果

                    if not user_exists:
                        print("用户不存在")  # 调试信息：用户不存在
                        return 1
                    query = f"SELECT * FROM book_with_borrow WHERE user_id = %s ORDER BY book_with_borrow.borrow_date DESC"
                    cursor.execute(query, (user_id,))
                    query_re = cursor.fetchall()
                connection.commit()
                print("Transaction committed successfully.")
                if (query_re is not None):
                    return query_re  # 返回成功状态
        except Exception as e:
            print(f"Error borrowing book: {e}")
            return None  # 返回失败状态
        finally:
            if connection:
                print("Closing database connection.")
                connection.close()

    def return_book(borrow_id):
        connection = None
        try:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                cursor.callproc('sp_return_book', (borrow_id,))
                # 获取结果
                result_set = cursor.fetchall()
                if result_set:  # 检查是否有结果
                    first_row = result_set[0]  # 取第一行
                    if isinstance(first_row, dict):  # 检查是否是字典格式
                        status = first_row.get('result')
                        message = first_row.get('message', '')
                        if status == 'success':
                            connection.commit()
                            print("Book returned successfully.")
                            return 1  # 成功状态
                        else:
                            print(f"Book already returned: {message}")
                            return 2  # 书籍已归还状态
                    else:
                        print("Unexpected result format - expected dictionary")
                        return 3  # 结果格式不符合预期
                else:
                    print("No results returned from the stored procedure.")
                    return 3  # 无结果返回

        except Exception as e:
            print(f"Error returning book: {e}")
            return 3  # 返回失败状态
        finally:
            if connection:
                if 'cursor' in locals():  # 确保cursor存在再关闭
                    cursor.close()
                print("Closing database connection.")
                connection.close()