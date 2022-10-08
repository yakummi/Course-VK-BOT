import psycopg2
from dataclasses import dataclass
from CourseVkBot.database.config import Settings

import vk_api
from CourseVkBot.bot_configs.token_user_vk import TOKEN_VK_USER
session = vk_api.VkApi(token=TOKEN_VK_USER)

conn = psycopg2.connect(database=Settings.DATABASE, user=Settings.USER, password=Settings.PASSWORD)


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
                            id_selection SERIAL PRIMARY KEY,
                            requester INT,
                            age INT,
                            country VARCHAR(100),
                            city VARCHAR(100),
                            gender VARCHAR(10)
                        );
                        ''')
            # ==================================================
            cur.execute(f'''
                        CREATE TABLE IF NOT EXISTS {self.tables_names['preferences']}(
                            id_preferences SERIAL PRIMARY KEY,
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
                            user_age INT,
                            id_selection INT references {self.tables_names['selection']} (id_selection) on delete set null,
                            id_preferences INT references {self.tables_names['preferences']} (id_preferences) on delete set null
                        );
                        ''')
            # ====================================================
            cur.execute(f'''
                       CREATE TABLE IF NOT EXISTS {self.tables_names['photos']}(
                           id_photo SERIAL PRIMARY KEY,
                           id_vk_user INT references {self.tables_names['users']} (id_vk_user) on delete set null,
                           link TEXT,
                           likes BOOLEAN
                       );
                        ''')
            conn.commit()
        # conn.close()

    def drop_tables(self):
        with conn.cursor() as cur:
            cur.execute(f'''
                DROP TABLE IF EXISTS {self.tables_names['selection']} CASCADE;
                DROP TABLE IF EXISTS {self.tables_names['preferences']} CASCADE;
                DROP TABLE IF EXISTS {self.tables_names['users']} CASCADE;
                DROP TABLE IF EXISTS {self.tables_names['photos']} CASCADE;
                ''')
            conn.commit()

    def insert_request(self, tables_name: str, current_request_values: list): # заносит поисковой запрос в БД
        with conn.cursor() as cur:
            cur.execute(f'''
                        INSERT INTO {self.tables_names[tables_name]} (requester, age, country, city, gender)
                        VALUES %s
                        RETURNING id_selection;
                        ''', (current_request_values,))
            id_sel = (cur.fetchone())[0]
            conn.commit()
        return id_sel

    def insert_base(self, tables_name1: str, tables_name2: str, tables_name3: str, preferences: list, id_selection: int, columns_values: list, photo_values: list): # заносит данные в БД по запросу
        with conn.cursor() as cur:
            cur.execute(f'''
                        INSERT INTO {self.tables_names[tables_name1]} (favorites, black_list, viewed)
                        VALUES %s
                        RETURNING id_preferences;
                        ''', (preferences,))
            id_pref = (cur.fetchone())[0]

            cur.execute(f'''
                        INSERT INTO {self.tables_names[tables_name2]} (id_vk_user, name, surname, user_age, id_selection, id_preferences) 
                        VALUES (%s,%s,%s,%s,%s,%s)
                        RETURNING id_vk_user;
                        ''', (columns_values[0], columns_values[1], columns_values[2], columns_values[3], id_selection, id_pref))
            id_vk = (cur.fetchone())[0]

            cur.execute(f'''
                        INSERT INTO {self.tables_names[tables_name3]} (id_vk_user, link, likes)
                        VALUES (%s, %s, %s);
                        ''', (id_vk, photo_values[0], photo_values[1]))
            conn.commit()
        # conn.close()

    def change_favorites(self, id_vk_user: int, favorites_status: bool): # меняет статус на избранный нужен id и ключ True
        with conn.cursor() as cur:
            cur.execute(f'''
                        UPDATE preferences SET favorites=%s
                        WHERE id_preferences=(SELECT id_preferences FROM users WHERE id_vk_user=%s);
                        ''', (favorites_status, id_vk_user))
            conn.commit()

    def change_black_list(self, id_vk_user: int, black_list: bool): # меняет статус на черный список нужен id и ключ True
        with conn.cursor() as cur:
            cur.execute(f'''
                        UPDATE preferences SET black_list=%s
                        WHERE id_preferences=(SELECT id_preferences FROM users WHERE id_vk_user=%s);
                        ''', (black_list, id_vk_user))
            conn.commit()

    def change_viewed(self, id_vk_user: int, viewed_status: bool): # меняет статус на просмотренный нужен id и ключ True
        with conn.cursor() as cur:
            cur.execute(f'''
                        UPDATE preferences SET viewed=%s
                        WHERE id_preferences=(SELECT id_preferences FROM users WHERE id_vk_user=%s);
                        ''', (viewed_status, id_vk_user))
            conn.commit()

    def show_favorites(self, favorites_status: bool): # показывает избранных если ключ True (без черного списка)
        with conn.cursor() as cur:
            cur.execute(f'''
                        SELECT name, surname, user_age, p.id_preferences FROM users u
                        JOIN preferences p ON u.id_preferences = p.id_preferences
                        WHERE favorites=%s and black_list=False;
                        ''', (favorites_status,))
            favorites_list = cur.fetchall()
        return favorites_list

    def show_black_list(self, black_list_status: bool): # показывает черный список если ключ True
        with conn.cursor() as cur:
            cur.execute(f'''
                        SELECT name, surname, user_age, p.id_preferences FROM users u
                        JOIN preferences p ON u.id_preferences = p.id_preferences
                        WHERE black_list=%s;
                        ''', (black_list_status,))
            black_list_list = cur.fetchall()
        return black_list_list

    def show_viewed(self, viewed_status: bool): # показывает просмотренных если ключ True (без черного списка)
        with conn.cursor() as cur:
            cur.execute(f'''
                        SELECT name, surname, user_age, p.id_preferences FROM users u
                        JOIN preferences p ON u.id_preferences = p.id_preferences
                        WHERE viewed=%s and black_list=False;
                        ''', (viewed_status,))
            viewed_list = cur.fetchall()
        return viewed_list
                        
#
# def user_db():
#     test = Database()


base = Database()
base.drop_tables()
base.create_tables()

