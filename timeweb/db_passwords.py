import sqlite3

conn = sqlite3.connect('blog.db')
cursor = conn.cursor()

cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords(
                login TEXT PRIMARY KEY,
                password TEXT NOT NULL)
''')

# Включаем поддержку внешних ключей
cursor.execute('PRAGMA foreign_keys = ON')

# добавление столбца
# Убирая NOT NULL, вы позволяете столбцу role принимать значения NULL, что означает, что значение может быть "пустым" (неопределенным).
# cursor.execute('''ALTER TABLE passwords ADD COLUMN role TEXT''')

# удаление столбца
# cursor.execute('''ALTER TABLE passwords DROP COLUMN role''')

# FOREIGN KEY (user_id)
# Эта часть указывает, что поле user_id в текущей таблице (таблице, где применяется это ограничение) является внешним ключом.
# Внешний ключ определяет, что значения в колонке user_id должны ссылаться на существующие значения в другой таблице.
# REFERENCES users (login)
# Это значит, что внешнее ключевое поле user_id указывает на поле login в таблице users. Таким образом, оно устанавливает
# связь между текущей таблицей и таблицей users. Значение в колонке user_id должно соответствовать значению, существующему
# в колонке login в таблице users.
# ON DELETE CASCADE
# Это поведение, задающее, что произойдет с записями в текущей таблице, если запись, на которую они ссылаются, будет удалена
# в таблице users.
# В данном случае, ON DELETE CASCADE означает, что если запись в таблице users с указанным значением login будет удалена,
# то все записи в текущей таблице, которые ссылаются на нее через внешние ключи (т. е. через поле user_id), также будут
# автоматически удалены. Таким образом, это помогает поддерживать целостность данных: система автоматически удаляет связанные
# записи, чтобы не осталось "висячих" ссылок.

# удаление таблицы
# cursor.execute('''DROP TABLE posts''')
cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный ID пользователя
                name TEXT, -- Имя пользователя
                email TEXT, -- Email пользователя
                role TEXT DEFAULT 'user',
                login TEXT NOT NULL, -- Логин, связанный с таблицей passwords
                FOREIGN KEY (login) REFERENCES passwords(login) ON DELETE CASCADE
)
''')

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


conn.commit()
conn.close()