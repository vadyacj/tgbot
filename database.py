import sqlite3

class BotDB:

    def __init__(self, db_file):
        """Инициализируем соед с бд"""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exist(self, user_id):
        """Проверка на наличие юзера в бд"""
        result = self.cursor.execute("SELECT 'id' FROM 'users' WHERE 'user_id' = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Получаем id по user_id в телеге"""
        result = self.cursor.execute("SELECT 'id' FROM 'users' WHERE 'user_id' = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id, name):
        """Добавляем юзера"""
        self.cursor.execute("INSERT INTO 'users' ('user_id', 'coins', 'status', 'name') VALUES (?, ?, ?, ?)", (user_id, 1000, 1, name))
        return self.conn.commit()

    def add_record(self, user_id, opperation, value):
        """Создаем запись о выигрыше иль проигрыше"""
        self.cursor.execute("INSERT INTO 'users' ('users_id', 'coins') VALUES (?, ?)",
                            self.get_user_id(user_id),
                            value)
        return self.conn.commit()

    def win(self, user_id, ourwin):
            self.cursor.execute(f"UPDATE users SET coins = {ourwin} WHERE user_id = {user_id}")

    def close(self):
        """Закрываем соединение"""
        self.conn.close()
