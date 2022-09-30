import psycopg2
from dataclasses import dataclass
from config import Settings

conn = psycopg2.connect(database=Settings.DATABASE, user=Settings.USER, password=Settings.PASSWORD)

@dataclass
class Database:
    # Названия таблиц
    tables_names = {'main_table': 'info_user',
                    'all_users': 'all_users',
                    'favorites_users': 'favorites_users'}


    def create_tables(self):
        with conn.cursor() as cur:
            cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tables_names['main_table']}(
            id INT not null generated always as identity primary key,
            name VARCHAR(100),
            surname VARCHAR(100),
            age INT,
            gender TEXT,
            city VARCHAR(100),
            country VARCHAR(150)
            );
            ''')
            # =======================================================
            cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tables_names['all_users']}(
            id INT,
            profile_id INT,
            name VARCHAR(100),
            surname VARCHAR(100),
            age INT,
            gender TEXT,
            city VARCHAR(100),
            country VARCHAR(150),
            photos TEXT,
            foreign key(id) references {self.tables_names['main_table']} (id) on delete set null 
            );
            ''')
            # ==================================================
            cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tables_names['favorites_users']}(
            id INT,
            profile_id INT,
            name VARCHAR(100),
            surname VARCHAR(100),
            age INT,
            gender TEXT,
            city VARCHAR(100),
            country VARCHAR(150),
            photos TEXT,
            foreign key(id) references {self.tables_names['main_table']} (id) on delete set null 
            );
            ''')
            conn.commit()
        conn.close()

    def drop_tables(self):
        with conn.cursor() as cur:
            cur.execute(f'''
            DROP TABLE {self.tables_names['main_table']} CASCADE;
            DROP TABLE {self.tables_names['all_users']} CASCADE;
            DROP TABLE {self.tables_names['favorites_users']} CASCADE;
            ''')
            conn.commit()
        conn.close()

def user_db():
    test = Database()

