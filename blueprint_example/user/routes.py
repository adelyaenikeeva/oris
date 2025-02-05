from flask import render_template, request, redirect, url_for, flash
from . import user_blueprint
from oris.timeweb.utils.database import get_db_connection

"""
    Flask Blueprint  - это способ разделения приложения на более мелкие, модульные компоненты, что помогает улучшить 
    читаемость кода, структурированность проекта и его масштабируемость.
    Основная идея заключается в том, чтобы вынести определённый функционал, маршруты и связанные с ними элементы в отдельный модуль, 
    а затем подключить их к основному приложению.
    
    Основные этапы организации приложения с Blueprint
    Создание модулей приложения:
    Например, модули для пользователей, постов, тегов, авторизации и регистрации.
    
    Создание структуры проекта:
    Каждый модуль будет представлять собой отдельную директорию с файлами для маршрутов, моделей, шаблонов и других ресурсов.
    
    Настройка Blueprint для каждого модуля:
    Каждый модуль будет использовать Blueprint для регистрации своих маршрутов.
    Реализация маршрутов каждого модуля.
    Регистрация Blueprints в основном приложении.
    
    Преимущества использования Flask Blueprint
    Разделение кода на независимые модули, которые проще поддерживать и тестировать.
    
    Возможность использования одного и того же Blueprint в нескольких приложениях.
    
    Компоненты, относящиеся к одной сущности (маршруты, формы, шаблоны), хранятся в одном месте.
"""


@user_blueprint.route("/user")
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM passwords').fetchall()
    conn.close()
    return render_template('users.html', users=users)


# Страница создания нового пользователя
@user_blueprint.route('/user/create_user', methods=('GET', 'POST'))
def create_user():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        conn = get_db_connection()
        conn.execute('INSERT INTO passwords (login, password) VALUES (?, ?)', (login, password))
        conn.execute('INSERT INTO user_profile (login) VALUES (?)', (login,))
        conn.commit()
        conn.close()

        return redirect(url_for('user.get_users'))

    return render_template('create_user.html')


# Страница редактирования пользователя
@user_blueprint.route('/user/<string:login>/edit_user', methods=('GET', 'POST'))
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
        return redirect(url_for('user.get_users'))

    conn.close()
    return render_template('edit_user.html', user=user)

# Удаление пользователя
@user_blueprint.route('/user/<string:login>/delete_user', methods=('POST',))
def delete_user(login):
    conn = get_db_connection()
    conn.execute('DELETE FROM passwords WHERE login = ?', (login,))
    conn.commit()
    conn.close()
    flash('Пользователь удален')
    return redirect(url_for('user.get_users'))