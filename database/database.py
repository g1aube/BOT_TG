import psycopg2

DB_NAME = '' # имя базы данных
DB_USER = '' # пользователь базы данных
DB_PASSWORD = '' # пароль от пользователя базы данных
DB_PORT = None # порт базы данных

database_tables = {
    'users': 'users',
    'admins': 'admins',
}

class DataBase:

    conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)

    # Функция создания таблиц для базы данных
    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {database_tables['users']} (
            id INT not null generated always as identity primary key,
            telegram_id BIGINT,
            user_name TEXT
            );
            """)

            self.conn.commit()

            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {database_tables['admins']} (
            id INT not null generated always as identity primary key,
            user_id BIGINT,
            FOREIGN KEY (user_id) REFERENCES {database_tables['users']}(id)
            );
            """)

            self.conn.commit()


    def add_user(self, telegram_id, username):
        with self.conn.cursor() as cur:
            cur.execute(f'''
            INSERT INTO {database_tables['users']} (telegram_id, user_name)
            VALUES({telegram_id}, {repr(username)});
            ''')

            self.conn.commit()

    def check_user(self, telegram_id, username):
        with self.conn.cursor() as cur:
            select = f"""
            SELECT *
            FROM {database_tables['users']}
            WHERE telegram_id = {telegram_id}
            """

            cur.execute(select)
            result = cur.fetchall()
            if result == []:
                self.add_user(telegram_id=telegram_id, username=username)
                self.conn.commit()

    def check_user_id(self, telegram_id):
        with self.conn.cursor() as cur:
            select = f"""
            SELECT id
            FROM {database_tables['users']}
            WHERE telegram_id = {telegram_id}
            """

            cur.execute(select)
            result = cur.fetchall()
            return result

    def check_admin(self, telegram_id):
        with self.conn.cursor() as cur:
            select = f"""
            SELECT *
            FROM {database_tables['admins']}
            WHERE user_id = {telegram_id}
            """

            cur.execute(select)
            result = cur.fetchall()
            return result
        
    def get_all_users(self):
        with self.conn.cursor() as cur:
            select = f"""
            SELECT *
            FROM {database_tables['users']}
            """

            cur.execute(select)
            result = cur.fetchall()

            return result
        
    def get_all_admins(self):
        with self.conn.cursor() as cur:
            select = f"""
            SELECT *
            FROM {database_tables['admins']}
            """

            cur.execute(select)
            result = cur.fetchall()

            return result


db = DataBase()
db.create_tables()