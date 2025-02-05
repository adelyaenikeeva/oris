import sqlite3

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('blog.db')
    # Возвращаем результаты в виде словарей
    conn.row_factory = sqlite3.Row
    return conn


# Функция для инициализации базы данных и создания таблиц
def init_db():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # добавление столбца
    # Убирая NOT NULL, вы позволяете столбцу role принимать значения NULL, что означает, что значение может быть "пустым" (неопределенным).
    # cursor.execute('''ALTER TABLE passwords ADD COLUMN role TEXT''')

    # удаление столбца
    # cursor.execute('''ALTER TABLE passwords DROP COLUMN role''')

    # FOREIGN KEY (user_id)
    # Эта часть указывает, что поле user_id в текущей таблице (таблице, где применяется это ограничение) является внешним ключом.
    # Внешний ключ определяет, что значения в колонке user_id должны ссылаться на существующие значения в другой таблице.
    # REFERENCES user (login)
    # Это значит, что внешнее ключевое поле user_id указывает на поле login в таблице user. Таким образом, оно устанавливает
    # связь между текущей таблицей и таблицей user. Значение в колонке user_id должно соответствовать значению, существующему
    # в колонке login в таблице user.
    # ON DELETE CASCADE
    # Это поведение, задающее, что произойдет с записями в текущей таблице, если запись, на которую они ссылаются, будет удалена
    # в таблице user.
    # В данном случае, ON DELETE CASCADE означает, что если запись в таблице user с указанным значением login будет удалена,
    # то все записи в текущей таблице, которые ссылаются на нее через внешние ключи (т. е. через поле user_id), также будут
    # автоматически удалены. Таким образом, это помогает поддерживать целостность данных: система автоматически удаляет связанные
    # записи, чтобы не осталось "висячих" ссылок.

    # cursor.execute('''DROP TABLE posts''')
    # удаление таблицы
    # cursor.execute('''DROP TABLE post_tags''')
    # cursor.execute('''DROP TABLE user_profile''')

    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS passwords(
                    login TEXT PRIMARY KEY,
                    password TEXT NOT NULL)
    ''')

    # Включаем поддержку внешних ключей
    cursor.execute('PRAGMA foreign_keys = ON')

    # Связь "один к одному" между таблицами passwords и user_profile реализована через поле login.
    # Каждому логину в таблице passwords соответствует ровно один профиль в таблице user_profile.
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profile (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный ID пользователя
                    name TEXT, -- Имя пользователя
                    email TEXT UNIQUE, -- Email пользователя
                    role TEXT DEFAULT 'user',
                    login TEXT NOT NULL UNIQUE,        -- Логин, который должен быть уникальным
                    FOREIGN KEY (login) REFERENCES passwords(login) ON DELETE CASCADE
    )
    ''')

    # Таблица user_profile имеет связь "один ко многим" с таблицей posts, поскольку один пользователь может создавать несколько постов,
    # но каждый пост ассоциирован только с одним пользователем. Это реализуется через поле user_id в таблице posts,
    # которое является внешним ключом, указывающим на уникальный идентификатор пользователя.
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    image_path TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profile (user_id) ON DELETE CASCADE
                )
    ''')

    # Таблица тегов
    # UNIQUE гарантирует отсутствие дубликатов тегов.
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
    )
    ''')

    # Связующая таблица для posts и tags
    # Связь "многие ко многим" реализуется через связующую таблицу post_tags.
    # Один пост может иметь много тегов, и один тег может быть связан с многими постами.
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS post_tags (
                    post_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    FOREIGN KEY (post_id) REFERENCES posts (post_id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE,
                    PRIMARY KEY (post_id, tag_id)
                )
    ''')

    conn.commit()
    conn.close()