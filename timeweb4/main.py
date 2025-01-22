import os

from flask import Flask, request, render_template, session, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Генерирует случайный 24-байтовый ключ

def get_db_connection():
    conn = sqlite3.connect('login_password.db')
    # Возвращаем строки как "словари"
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    if request.method == 'POST':
        login = request.form.get('Login')
        password = request.form.get('Password')

        # Подключаемся к базе данных
        db_lp = sqlite3.connect('login_password.db')
        cursor_db = db_lp.cursor()

        # Используем параметризованный SQL-запрос, чтобы избежать SQL-инъекций.
        # Здесь вместо значений вставляются специальные плейсхолдеры (? в случае SQLite) или их эквиваленты для других СУБД.
        # Значения для этих плейсхолдеров передаются в виде отдельного списка или кортежа.
        # Преимущества:
        # Защита от SQL-инъекций. Данные из переменных (login, password) не интерпретируются как часть SQL-запроса,
        # а передаются отдельно — как данные. СУБД автоматически экранирует любые опасные символы вроде одинарных кавычек (')
        # или других, предотвращая возможное выполнение вредоносного SQL-кода.

        cursor_db.execute('SELECT password FROM passwords WHERE login = ?', (login,))
        result = cursor_db.fetchone()

        # Проверяем, существует ли пользователь
        if not result:
            return render_template('auth/authorization.html', error_message="Пользователя с таким логином не существует!")

        # Проверяем, совпадает ли пароль
        if result[0] != password:
            return render_template('auth/authorization.html', error_message="Неверный пароль!")

        # # Если логин и пароль верны, извлекаем роль пользователя
        # cursor_db.execute('SELECT role FROM passwords WHERE login = ?', (login,))
        # role = cursor_db.fetchone()[0]
        #
        # # Сохраняем данные в сессии только после успешной авторизации
        # session['username'] = login
        # session['role'] = role

        # Закрываем подключение к базе данных
        db_lp.close()

        # Если всё прошло успешно
        return redirect(url_for('index'))

    return render_template('auth/authorization.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
   if request.method == 'POST':
       Login = request.form.get('Login')
       Password = request.form.get('Password')

       db_lp = sqlite3.connect('login_password.db')
       cursor_db = db_lp.cursor()

       cursor_db.execute('INSERT INTO passwords (login, password) VALUES (?, ?)', (Login, Password))

       db_lp.commit()
       db_lp.close()

       return redirect(url_for('authorization'))

   return render_template('auth/registration.html')

@app.route('/')
def index():
    return render_template('main/index.html')

@app.route("/about")
def about():
    return render_template("main/about.html")

@app.route("/users")
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM passwords').fetchall()
    conn.close()
    return render_template('users/users.html', users=users)

@app.route('/account', methods=('GET', 'POST'))
def account():
    return render_template('account/account.html')

# Страница создания нового поста
@app.route('/create_users', methods=('GET', 'POST'))
def create_users():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        conn = get_db_connection()
        conn.execute('INSERT INTO passwords (login, password) VALUES (?, ?)', (login, password))
        conn.commit()
        conn.close()

        return redirect(url_for('get_users'))

    return render_template('create.html')

# Страница редактирования поста
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
        conn.commit()
        conn.close()
        return redirect(url_for('get_users'))

    return render_template('edit.html', post=post)

# Удаление поста
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Post has been deleted.')
    return redirect(url_for('get_users'))

@app.route('/logout')
def logout():
    # Удаляем имя пользователя из сессии (выход из аккаунта)
    session.pop('username', None)
    session.clear()  # Очистка всех данных сессии
    return redirect(url_for('index'))


# @app.route('/user_posts')
# def user_posts():
#     # Проверяем, авторизован ли пользователь
#     if 'username' not in session:
#         return redirect(url_for('login'))  # Если не авторизован, перенаправляем на страницу входа
#
#     username = session['username']
#
#     # Получаем ID пользователя из таблицы passwords на основе имени пользователя (линк с таблицей posts)
#     conn = get_db_connection()
#
#     user_id = conn.execute('SELECT id FROM passwords WHERE login = ?', (username,)).fetchone()
#     if user_id is None:
#         conn.close()
#         return redirect(url_for('login'))  # Если пользователя не существует, перенаправляем на страницу входа
#
#     # Получаем только те посты, которые принадлежат текущему пользователю
#     posts = conn.execute('SELECT * FROM posts WHERE user_id = ?', (user_id['id'],)).fetchall()
#     conn.close()
#
#     # Рендерим страницу для просмотра "Мои посты"
#     return render_template('user_posts.html', posts=posts, username=username)

if __name__ == "__main__":
    app.run(port=5001)