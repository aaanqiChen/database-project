from flask import Flask, request, redirect, url_for, flash, render_template, session, jsonify, make_response
import pymysql
from pymysql import cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于flash消息

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


@app.route('/register', methods=['POST'])
def register():
    # 获取表单数据
    username = request.form['username']
    password = request.form['password']
    contact = request.form['contact']

    try:
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                # 插入数据的SQL语句
                insert_sql = """
                             INSERT INTO user(user_name, password, phone)
                             VALUES (%s, %s, %s) \
                             """
                cursor.execute(insert_sql, (username, password, contact))
            connection.commit()
            flash('register success!', 'success')
            return redirect(url_for('login_page'))
    except Exception as e:
        flash('failed!name is exist', 'error')
        return redirect(url_for('login_page'))
    finally:
        if connection and connection.open:
            connection.close()


@app.route('/register_page')
def register_page():
    return render_template('register.html')

@app.route('/management_page')
def management_page():
    return render_template('management.html')


@app.route('/')
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    # 记录请求开始
    app.logger.debug('开始处理登录请求')
    app.logger.debug(
        f'接收到的表单数据: username={request.form.get("username")}, password={request.form.get("password")}')

    username = request.form['username']
    password = request.form['password']

    try:
        connection = get_db_connection()
        app.logger.debug(f'数据库连接状态: {"已建立" if connection else "失败"}')

        if connection:
            with connection.cursor() as cursor:
                # 首先检查用户是否存在
                query_user_sql = """
                                 SELECT *
                                 FROM user
                                 WHERE user_name = %s \
                                 """
                app.logger.debug(f'执行SQL查询: {query_user_sql}，参数: {username}')
                cursor.execute(query_user_sql, (username,))
                user = cursor.fetchone()
                app.logger.debug(f'查询用户结果: {user}')

                if not user:
                    flash('该用户不存在', 'error')
                    app.logger.warning(f'登录失败: 用户不存在 - {username}')
                    return redirect(url_for('login_page'))

                # 用户存在，检查密码
                app.logger.debug(f'数据库中的密码: {user["password"]}, 输入的密码: {password}')
                if user['password'] != password:
                    flash('密码错误', 'error')
                    app.logger.warning(f'登录失败: 密码错误 - 用户名: {username}')
                    return redirect(url_for('login_page'))

                # 密码正确，获取用户详细信息
                query_user_data_sql = """
                                      SELECT u.user_name, r.brief_intro, r.can_borrow_num, r.credit_level
                                      FROM user u
                                               JOIN reader r ON u.user_id = r.user_id
                                      WHERE u.user_name = %s \
                                      """
                app.logger.debug(f'执行读者信息查询: {query_user_data_sql}，参数: {username}')
                cursor.execute(query_user_data_sql, (username,))
                user_data = cursor.fetchone()
                app.logger.debug(f'读者信息查询结果: {user_data}')

                if not user_data:
                    query_user_data_sql = """
                                          SELECT u.user_name, m.access_level, m.management_scope, m.department
                                          FROM user u
                                                   JOIN manager m ON u.user_id = m.user_id
                                          WHERE u.user_name = %s \
                                          """
                    app.logger.debug(f'执行管理员信息查询: {query_user_data_sql}，参数: {username}')
                    cursor.execute(query_user_data_sql, (username,))
                    user_data2 = cursor.fetchone()
                    app.logger.debug(f'管理员信息查询结果: {user_data2}')

                    # 登录成功，设置会话
                    session['user_id'] = user['user_id']
                    session['username'] = user['user_name']
                    session['logged_in'] = True
                    app.logger.info(f'管理员登录成功: 用户名: {username}, ID: {user["user_id"]}')

                    # 重定向到读者页面并传递用户数据
                    return render_template('admin_1.html',
                                           username=user_data2['user_name'],
                                           access_level=user_data2['access_level'],
                                           management_scope=user_data2['management_scope'],
                                           department=user_data2['department'])

                # 登录成功，设置会话
                session['user_id'] = user['user_id']
                session['username'] = user['user_name']
                session['logged_in'] = True
                app.logger.info(f'读者登录成功: 用户名: {username}, ID: {user["user_id"]}')

                # 重定向到读者页面并传递用户数据
                return render_template('reader_1.html',
                                       username=user_data['user_name'],
                                       bio=user_data['brief_intro'],
                                       books_available=user_data['can_borrow_num'],
                                       credit_record=user_data['credit_level'])

    except Exception as e:
        app.logger.error(f'登录过程中发生错误: {str(e)}', exc_info=True)
        flash(f'登录过程中发生错误: {str(e)}', 'error')
        return redirect(url_for('login_page'))
    finally:
        if connection and connection.open:
            connection.close()
            app.logger.debug('数据库连接已关闭')

    flash('登录失败', 'error')
    app.logger.warning('登录流程异常结束，未返回任何响应')
    return redirect(url_for('login_page'))

@app.route('/reader_page')
def reader_page():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login_page'))

    try:
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                # 获取用户详细信息
                query_user_data_sql = """
                                      SELECT u.user_name, r.brief_intro, r.can_borrow_num, r.credit_level
                                      FROM user u
                                               JOIN reader r ON u.user_id = r.user_id
                                      WHERE u.user_name = %s \
                                      """
                cursor.execute(query_user_data_sql, (session['username'],))
                user_data = cursor.fetchone()

                if not user_data:
                    flash('用户信息不完整', 'error')
                    return redirect(url_for('login_page'))

                return render_template('reader_1.html',
                                       username=user_data['user_name'],
                                       bio=user_data['brief_intro'],
                                       books_available=user_data['can_borrow_num'],
                                       credit_record=user_data['credit_level'])

    except Exception as e:
        flash(f'获取用户信息时发生错误: {str(e)}', 'error')
        return redirect(url_for('login_page'))
    finally:
        if connection and connection.open:
            connection.close()

    flash('无法获取用户信息', 'error')
    return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
    session.clear()
    flash('您已成功登出', 'success')
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True)

 //cursor.execute("SELECT cate_table FROM category WHERE category_id = %s", (category,))
        //cate_table = cursor.fetchone()['cate_table']
        //cursor.execute(
            //'INSERT INTO {cate_table} (book_name,writer_id,publisher,publish_date,price,stock,borrow_hot,bookcase_id,language,total_amount,brief_intro,catagory_id) VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s)',
            //(book_name, writer_id, publisher, publish_date, price, stock, borrow_hot, bookcase_id, language,
             //total_amount, brief_intro, catagory))