from flask import Blueprint, render_template_string, request, jsonify, session

admin_bp = Blueprint('admin', __name__)

# 模拟数据库
books = [
    {'id': 1, 'title': 'Book 1', 'author': 'Author 1'},
    {'id': 2, 'title': 'Book 2', 'author': 'Author 2'}
]

@admin_bp.route('/')
def main_page():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Library Management System - Admin Home</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    background-image: url('{{ url_for("static", filename="admin_1.png") }}');
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                }
                /* 其余样式保持不变... */
            </style>
        </head>
        <body>
            <!-- 原有HTML内容保持不变... -->
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script>
                function loadContent(page) {
                    if (!page) {
                        console.error('Invalid page parameter');
                        return;
                    }
                    $.get(`/admin/${page}`, function(data) {  // 注意这里改为/admin/前缀
                        $('#contentArea').html(data);
                    });
                }
            </script>
        </body>
        </html>
    ''', username=session.get('username', '管理员'))

@admin_bp.route('/book-management')
def book_management():
    return render_template_string('''
        <div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
            <h2>图书管理</h2>
            <button onclick="addBook()">增加图书</button>
            <button onclick="deleteBook()">删减图书</button>
            <button onclick="searchBook()">检索图书</button>
            <button onclick="countBooks()">统计图书数量</button>
        </div>
        <script>
            function addBook() {
                alert('增加图书功能');
            }
            function deleteBook() {
                alert('删减图书功能');
            }
            function searchBook() {
                alert('检索图书功能');
            }
            function countBooks() {
                alert('统计图书数量功能');
            }
        </script>
    ''')