from flask import Flask, request, redirect, url_for, flash, render_template,render_template_string, session, jsonify, make_response
import pymysql
from pymysql import cursors
from database.connection import get_db_connection
from models.book import Book
from models.fine import Fine
from services.book_service import add_book
from services.user_service import add_user
from models.user import User

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于flash消息


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        contact = request.form['contact']

        if User.add_user(username, password, contact):
            flash('Registration successful!', 'success')
            return redirect(url_for('login_page'))
        else:
            flash('Failed! Username already exists.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    # 记录请求开始
    app.logger.debug('开始处理登录请求')
    app.logger.debug(
        f'接收到的表单数据: username={request.form.get("username")}, password={request.form.get("password")}')

    username = request.form['username']
    password = request.form['password']

    if not User.is_user_in(username):
        flash('该用户不存在', 'error')
        return redirect(url_for('login_page'))

    # 用户存在，检查密码
    if not User.is_user_pw(username,password):
        flash('密码错误', 'error')
        return redirect(url_for('login_page'))
    user_data=User.query_user_data(username)
    if not user_data:
        user_data2=User.query_muser_data(username)
        # 登录成功，设置会话
        session['username'] = user_data2['user_name']
        session['logged_in'] = True
        # 重定向到读者页面并传递用户数据
        return render_template('admin_1.html',
                               username=user_data2['user_name'],
                               access_level=user_data2['access_level'],
                               management_scope=user_data2['management_scope'],
                               department=user_data2['department'])

    # 登录成功，设置会话
    session['username'] = user_data['user_name']
    session['logged_in'] = True
    session['user_id']=user_data['user_id']

    # 重定向到读者页面并传递用户数据
    return render_template('reader_1.html',
                           user_id=user_data['user_id'],
                           username=user_data['user_name'],
                           bio=user_data['brief_intro'],
                           books_available=user_data['can_borrow_num'],
                           credit_record=user_data['credit_level'])

    flash('登录失败', 'error')
    app.logger.warning('登录流程异常结束，未返回任何响应')
    return redirect(url_for('login_page'))


@app.route('/search_nabook', methods=['POST'])
def search_nabook():
    book_title = request.form.get('bookTitle')
    print(book_title)
    results = Book.query_nabook1(book_title)
    if not results:
        # 如果没有结果，返回提示信息
        return render_template('no_book.html')
    else:
        # 如果有结果，渲染子页面显示查询结果
        return render_template('book_results_1.html', books=results)
@app.route('/search_author', methods=['POST'])
def search_author():
    author_name = request.form.get('authorName')
    print(author_name)
    results = Book.query_wrbook1(author_name)
    if not results:
        # 如果没有结果，返回提示信息
        return render_template('no_book.html')
    else:
        # 如果有结果，渲染子页面显示查询结果
        return render_template('book_results_1.html', books=results)


@app.route('/add_book2', methods=['POST'])
def add_book2():
    # 获取表单数据
    book_name = request.form.get('book_name')
    book_writer = request.form.get('book_writer')
    publisher = request.form.get('publisher')
    publish_data = request.form.get('publish_data')
    price = request.form.get('price')
    bookcase = request.form.get('bookcase')
    language = request.form.get('language')
    brief_intro = request.form.get('brief_intro')
    total_amount = request.form.get('total_amount')
    category = request.form.get('category')
    Book.add_book(book_name,book_writer,publisher,publish_data,price,bookcase,language,total_amount,brief_intro,category)
    return render_template('add_book.html', success=True)


@app.route('/remove_user2', methods=['POST'])
def remove_user2():
    user_id = request.form.get('user_id')
    result=User.is_user_delete(user_id)
    print(result)
    if result==3:
        return jsonify({'success': True, 'message': '删除成功'})
    if result==1:
        return jsonify({'success': False, 'message': '当前用户不存在'})
    if result==2:
        return jsonify({'success': False, 'message': '当前用户存在未还书籍，不能删除！'})
    if result==4:
        return jsonify({'success': False, 'message': '删除失败'})


@app.route('/return_book', methods=['POST'])
def return_book():
    borrow_id = request.form.get('borrow_id')
    print(borrow_id)
    result = Book.return_book(borrow_id)

    if result == 1:
        return jsonify({'message': '还书成功'})
    elif result == 2:
        return jsonify({'message': '当前未借阅该书'})
    else:
        return jsonify({'message': '还书失败'})

@app.route('/borrow_query')
def borrow_query():
    user_id = session.get('user_id')  # 假设从请求中获取用户 ID
    borrow_records = Book.get_borrow_records(user_id)
    print(borrow_records)# 假设这是从数据库中获取借阅记录的函数
    return render_template('reader_borrow_query.html', borrow_records=borrow_records)

@app.route('/search_borrow', methods=['POST'])
def search_borrow():
    user_id1= request.form.get('userId')
    print(user_id1)
    user_id=int(user_id1)# 假设从请求中获取用户 ID
    borrow_records = Book.get_borrow_records(user_id)
    print(borrow_records)# 假设这是从数据库中获取借阅记录的函数
    if borrow_records==1:
        return render_template('no_user.html')
    else:
        return render_template('user_borrow_results.html', borrow_result=borrow_records)
@app.route('/search_no_borrow_users', methods=['POST'])
def search_no_borrow_users():
    user_records = User.query_noborrow_user()
    print(user_records)# 假设这是从数据库中获取借阅记录的函数
    return render_template('user_results.html', users_result=user_records)
@app.route('/get_all_users', methods=['POST'])
def get_all_users():
    user_records = User.get_all_users()
    print(user_records)# 假设这是从数据库中获取借阅记录的函数
    return render_template('user_results.html', users_result=user_records)
@app.route('/get_all_fines', methods=['POST'])
def get_all_fines():
    user_id=session.get('user_id')
    fine_records = Fine.get_all_fines(user_id)
    print(fine_records)# 假设这是从数据库中获取借阅记录的函数
    return render_template('fine_results.html', fine_result=fine_records)


@app.route('/fine_query', methods=['POST'])
def fine_query():
    user_id = session.get('user_id')  # 假设从请求中获取用户 ID
    results= Book.get_fine_records(user_id)
    print(results)
    if results is None:
        # 如果没有结果，返回提示信息
        app.logger.debug("No results found, rendering 'no_book.html'")
        return render_template('no_book.html')
    else:
        # 如果有结果，渲染子页面显示查询结果
        app.logger.debug("Results found, rendering 'book_results_1.html'")
        return render_template('book_results_1.html', books=results)


@app.route('/update_bio', methods=['POST'])
def update_bio():
    user_id = request.form.get('user_id')
    bio = request.form.get('bio')

    try:
        User.update_user_bio_in_database(user_id, bio)
        return jsonify({'message': '简介更新成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/borrow_book')
def borrow_book():
    book_id = request.args.get('book_id')
    user_id = session.get('user_id')
    in_user_id=request.args.get('user_id')
    if(int(in_user_id)!=user_id):
        return render_template('borrow_message.html', message='请输入正确id')
    try:
        Book.borrow_book(book_id, user_id)
        return render_template('borrow_message.html', message='借阅成功！')
    except Exception as e:
        return render_template('borrow_message.html', message=str(e))

@app.route('/reader_page')
def reader_page():
    return redirect(url_for('login_page'))


@app.route('/reader_borrow_query')
def reader_borrow_query():
    # 你的视图逻辑
    return render_template('reader_borrow_query.html')
@app.route('/user_results')
def user_results():
    # 你的视图逻辑
    return render_template('user_results.html')
@app.route('/fine_results')
def fine_results():
    # 你的视图逻辑
    return render_template('fine_results.html')
@app.route('/no_user')
def no_user():
    # 你的视图逻辑
    return render_template('no_user.html')
@app.route('/reader_query_allfine')
def reader_query_allfine():
    # 你的视图逻辑
    return render_template('reader_query_allfine.html')
@app.route('/no_borrow_user')
def no_borrow_user():
    # 你的视图逻辑
    return render_template('no_borrow_user.html')
@app.route('/all_user_data')
def all_user_data():
    # 你的视图逻辑
    return render_template('all_user_data.html')
@app.route('/user_borrow_book')
def user_borrow_book():
    # 你的视图逻辑
    return render_template('user_borrow_book.html')
@app.route('/reader_query_fine')
def reader_query_fine():
    # 你的视图逻辑
    return render_template('reader_query_fine.html')
@app.route('/query_allborrow')
def query_allborrow():
    # 你的视图逻辑
    return render_template('query_allborrow')
@app.route('/user_borrow_results')
def user_borrow_results():
    # 你的视图逻辑
    return render_template('user_borrow_results')
@app.route('/register_page')
def register_page():
    return render_template('register.html')

@app.route('/management_page')
def management_page():
    return render_template('management.html')

@app.route('/borrow_message_page')
def borrow_message_page():
    return render_template('borrow_message.html')

@app.route('/book-management')
def book_management():
    return render_template('book_management.html')  # 确保有一个book_management.html模板文件

@app.route('/remove_user')
def remove_user():
    return render_template('remove_user.html')  # 确保有一个book_management.html模板文件

@app.route('/user-management')
def user_management():
    return render_template('user_management.html')
@app.route('/borrow-management')
def borrow_management():
    return render_template('borrow_management.html')
@app.route('/fine-management')
def fine_management():
    return render_template('fine_management.html')


@app.route('/add-book')
def add_book():
    return render_template('add_book.html')

@app.route('/book_results_1')
def book_results_1():
    return render_template('book_results_1.html')


@app.route('/no-book')
def no_book():
    return render_template('no_book.html')

@app.route('/reader_query_nabook')
def reader_query_nabook():
    return render_template('reader_query_nabook.html')


@app.route('/reader_query_book')
def reader_query_book():
    return render_template('reader_query_book.html')


@app.route('/reader_query_wrbook')
def reader_query_wrbook():
    return render_template('reader_query_wrbook.html')


@app.route('/remove-book')
def remove_book():
    return render_template('remove_book.html')
@app.route('/')
def login_page():
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('您已成功登出', 'success')
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True)