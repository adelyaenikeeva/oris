from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'admin123'

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('blog.db')
    # Возвращаем строки как "словари"
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация базы данных
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        conn.commit()

# Главная страница с выводом постов
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('crud_example/index.html', posts=posts)

# Страница создания нового поста
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        conn = get_db_connection()
        conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('crud_example/create.html')

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
        return redirect(url_for('index'))

    return render_template('crud_example/edit.html', post=post)

# Удаление поста
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Post has been deleted.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # init_db()
    app.run(port=5001)