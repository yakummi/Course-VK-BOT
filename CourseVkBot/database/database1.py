import psycopg2
from dataclasses import dataclass
from config import Settings
import vk_api
from bot_configs.token_user_vk import TOKEN_VK_USER
conn = psycopg2.connect(database=Settings.DATABASE, user=Settings.USER, password=Settings.PASSWORD)

session = vk_api.VkApi(token=TOKEN_VK_USER)


@dataclass
class Database:
    # Названия таблиц
    tables_names = {'users': 'users',
                    'selection': 'selection',
                    'preferences': 'preferences',
                    'photos': 'photos'}

    def create_tables(self):
        with conn.cursor() as cur:
            cur.execute(f'''
                        CREATE TABLE IF NOT EXISTS {self.tables_names['selection']}(
                            id_selection INT not null generated always as identity primary key,
                            age INT,
                            gender VARCHAR(10),
                            city VARCHAR(100),
                            country VARCHAR(100)
                        );
                        ''')
            # ==================================================
            cur.execute(f'''
                        CREATE TABLE IF NOT EXISTS {self.tables_names['preferences']}(
                            id_preferences INT not null generated always as identity primary key,
                            favorites BOOLEAN,
                            black_list BOOLEAN,
                            viewed BOOLEAN
                       );
                       ''')
            # ==================================================
            cur.execute(f'''
                        CREATE TABLE IF NOT EXISTS {self.tables_names['users']}(
                            id_vk_user INT not null primary key,
                            name VARCHAR(100),
                            surname VARCHAR(100),
                            id_selection INT references {self.tables_names['selection']} (id_selection) on delete set null,
                            id_preferences INT references {self.tables_names['preferences']} (id_preferences) on delete set null
                        );
                        ''')
            # ====================================================
            cur.execute(f'''
                       CREATE TABLE IF NOT EXISTS {self.tables_names['photos']}(
                           id_photo INT,
                           id_vk_user INT references {self.tables_names['users']} (id_vk_user) on delete set null,
                           link TEXT,
                           likes BOOLEAN
                       );
                        ''')
            conn.commit()
        conn.close()

    def drop_tables(self):
        with conn.cursor() as cur:
            cur.execute(f'''
            DROP TABLE {self.tables_names['users']} CASCADE;
            DROP TABLE {self.tables_names['selection']} CASCADE;
            # DROP TABLE {self.tables_names['preferences']} CASCADE;
            ''')
            conn.commit()
        conn.close()


def user_db():
    test = Database()

