from flask import Flask, request, render_template, session, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename  # Импортируем функцию secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Генерирует случайный 24-байтовый ключ
# Конфигурация для загрузки мультимедиа
# Это директория на сервере, где будут храниться все загружаемые файлы.
UPLOAD_FOLDER = 'static/uploads'
# Здесь в конфиг приложения Flask передается информация о директории для загрузок (UPLOAD_FOLDER).
# Это стандартный подход в Flask для работы с настройками, связанными с загрузкой файлов.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Разрешенные расширения файлов

# Функция проверки расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('blog.db')
    # Позволяет возвращать результаты в виде словарей
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        # Подключаемся к базе данных
        conn = sqlite3.connect('blog.db')
        cursor_db = conn.cursor()

        # Используем параметризованный SQL-запрос, чтобы избежать SQL-инъекций.
        # Здесь вместо значений вставляются специальные плейсхолдеры (? в случае SQLite) или их эквиваленты для других СУБД.
        # Значения для этих плейсхолдеров передаются в виде отдельного списка или кортежа.
        # Преимущества:
        # Данные из переменных (login, password) не интерпретируются как часть SQL-запроса,
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

        # Если логин и пароль верны, извлекаем роль пользователя
        cursor_db.execute('SELECT role FROM user_profile WHERE login = ?', (login,))
        role = cursor_db.fetchone()[0]
        # print(role)

        cursor_db.execute('SELECT user_id FROM user_profile WHERE login = ?', (login,))
        user_id = cursor_db.fetchone()[0]

        # Сохраняем данные в сессии только после успешной авторизации
        session['username'] = login
        session['role'] = role
        session['user_id'] = user_id

        # Закрываем подключение к базе данных
        conn.close()

        # Если всё прошло успешно
        return redirect(url_for('index'))

    return render_template('auth/authorization.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
   if request.method == 'POST':
       login = request.form.get('login')
       password = request.form.get('password')

       conn = sqlite3.connect('blog.db')
       cursor_db = conn.cursor()

       cursor_db.execute('INSERT INTO passwords (login, password) VALUES (?, ?)', (login, password))
       cursor_db.execute('INSERT INTO user_profile (login) VALUES (?)', (login, ))

       conn.commit()
       conn.close()

       return redirect(url_for('authorization'))

   return render_template('auth/registration.html')

@app.route('/')
def index():
    conn = get_db_connection()
    # INNER JOIN user_profile ON posts.user_id = user_profile.user_id:
    # Этот JOIN используется для соединения таблицы постов (posts) с таблицей пользовательских профилей (user_profile).
    # Он возвращает только те записи, для которых есть соответствие в обеих таблицах. То есть посты, у которых есть пользователь.
    # LEFT JOIN post_tags ON posts.post_id = post_tags.post_id:
    # LEFT JOIN позволяет извлекать все записи из таблицы posts, даже если для них нет соответствующих записей в таблице post_tags.
    # Это нужно для того, чтобы включить посты, у которых на данный момент нет тегов.
    # LEFT JOIN tags ON post_tags.tag_id = tags.tag_id:
    # Этот LEFT JOIN связывает таблицу тегов (tags) с промежуточной таблицей (post_tags), которая хранит связи между постами и тегами.
    # Это позволяет нам получить названия тегов, связанных с этими постами.

    # Поскольку один пост может иметь несколько тегов, мы используем функцию GROUP_CONCAT, чтобы собрать все связанные с постом теги в одну строку.
    # Это создаст строку, которую вы сможете отобразить на странице как список тегов для каждого поста.

    # Наконец, мы добавляем GROUP BY posts.post_id. Это необходимо для того, чтобы SQL-сервер понимал, что мы группируем результаты по уникальному идентификатору постов.
    posts_data = conn.execute('''
            SELECT
                posts.post_id,
                posts.title,
                posts.content,
                posts.image_path,
                user_profile.login,
                GROUP_CONCAT(tags.name, ', ') AS tags -- Группируем теги через запятую
            FROM posts
            INNER JOIN user_profile ON posts.user_id = user_profile.user_id
            LEFT JOIN post_tags ON posts.post_id = post_tags.post_id
            LEFT JOIN tags ON post_tags.tag_id = tags.id
            GROUP BY posts.post_id -- Группируем данные по ID поста
        ''').fetchall()
    conn.close()
    return render_template('main/index.html', posts=posts_data)

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
    conn = get_db_connection()
    current_login = session['username']
    user = conn.execute('SELECT login, name, email FROM user_profile WHERE login = ?', (current_login,)).fetchone()

    if request.method == 'POST':
        # login = request.form.get('login')
        name = request.form.get('name')
        email = request.form.get('email')

        conn.execute('UPDATE user_profile SET name = ?, email = ? WHERE login = ?', (name, email, current_login))
        conn.commit()
        conn.close()
        flash('Данные успешно обновлены')
        return redirect(url_for('account'))

    conn.close()
    return render_template('account/account.html', user=user)

# Страница создания нового пользователя
@app.route('/users/create_user', methods=('GET', 'POST'))
def create_user():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        conn = get_db_connection()
        conn.execute('INSERT INTO passwords (login, password) VALUES (?, ?)', (login, password))
        conn.execute('INSERT INTO user_profile (login) VALUES (?)', (login,))
        conn.commit()
        conn.close()

        return redirect(url_for('get_users'))

    return render_template('users/create_user.html')

# Страница редактирования пользователя
@app.route('/users/<string:login>/edit_user', methods=('GET', 'POST'))
def edit_user(login):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM passwords WHERE login = ?', (login,)).fetchone()

    if request.method == 'POST':
        new_login = request.form.get('login')
        new_password = request.form.get('password')

        conn.execute('UPDATE passwords SET login = ?, password = ? WHERE login = ?',
                     (new_login, new_password, login))
        conn.commit()
        conn.close()
        return redirect(url_for('get_users'))

    conn.close()
    return render_template('users/edit_user.html', user=user)

# Удаление пользователя
@app.route('/user/<string:login>/delete_user', methods=('POST',))
def delete_user(login):
    conn = get_db_connection()
    conn.execute('DELETE FROM passwords WHERE login = ?', (login,))
    conn.commit()
    conn.close()
    flash('Пользователь удален')
    return redirect(url_for('get_users'))

@app.route('/logout')
def logout():
    # Удаляем имя пользователя из сессии (выход из аккаунта)
    session.pop('username', None)
    session.clear()  # Очистка всех данных сессии
    return redirect(url_for('index'))

@app.route('/user_posts')
def get_user_posts():
    conn = get_db_connection()

    # Получение данных о постах и тегах
    posts_data = conn.execute('''
           SELECT
               posts.post_id,
               posts.title,
               posts.content,
               posts.image_path,
               user_profile.login,
               GROUP_CONCAT(tags.name, ', ') AS tags
           FROM posts
           INNER JOIN user_profile ON posts.user_id = user_profile.user_id
           LEFT JOIN post_tags ON posts.post_id = post_tags.post_id
           LEFT JOIN tags ON post_tags.tag_id = tags.id
           WHERE user_profile.login = ?
           GROUP BY posts.post_id, user_profile.login
       ''', (session['username'],)).fetchall()

    conn.close()
    return render_template('user_posts/user_posts.html', posts=posts_data)


@app.route('/create_user_post', methods=('GET', 'POST'))
def create_user_post():
    if request.method == 'POST':
        # Получение данных из формы
        title = request.form.get('title')
        content = request.form.get('content')
        selected_tags = request.form.getlist('tags')  # Получаем список выбраных тегов
        user_id = session.get('user_id')
        file = request.files.get('image')  # Получение загружаемого файла

        # Обработка загружаемого файла
        image_path = None
        # проверяется, существует ли файл (file) и соответствует ли его имя установленным требованиям (например, расширения файла).
        if file and allowed_file(file.filename):
            safe_filename = secure_filename(file.filename)
            # Указываем безопасный путь для сохранения файла
            # Все действия с файлом теперь происходят только через безопасное имя safe_filename.
            upload_path = f'static/uploads/{safe_filename}'

            # Сохраняем файл по безопасному пути
            file.save(upload_path)

            # Сохраняем путь к файлу в переменную для дальнейшего использования
            image_path = upload_path

        # Сохранение в SQLite
        try:
            conn = sqlite3.connect('blog.db')
            cursor = conn.cursor()

            # Вставляем новые данные в таблицу posts
            cursor.execute('''
                    INSERT INTO posts (user_id, title, content, image_path)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, title, content, image_path))

            post_id = cursor.lastrowid  # Получаем ID созданного поста

            # Добавляем теги для поста в таблицу post_tags
            for tag_id in selected_tags:
                cursor.execute('''
                                INSERT INTO post_tags (post_id, tag_id)
                                VALUES (?, ?)
                            ''', (post_id, tag_id))

            conn.commit()
            conn.close()

            flash('Пост успешно добавлен!', 'success')
            return redirect(url_for('get_user_posts'))
        except Exception as e:
            flash(f'Ошибка при добавлении поста: {str(e)}', 'danger')

    # Динамически загружаем доступные теги
    conn = get_db_connection()
    tags = conn.execute('SELECT id, name FROM tags').fetchall()
    conn.close()

    return render_template('user_posts/create_user_post.html', tags=tags)

if __name__ == "__main__":
    app.run(port=5002)