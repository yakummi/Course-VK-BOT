import psycopg2
from dataclasses import dataclass
from CourseVkBot.database.config import Settings
import vk_api
from CourseVkBot.bot_configs.token_user_vk import TOKEN_VK_USER
conn = psycopg2.connect(database=Settings.DATABASE, user=Settings.USER, password=Settings.PASSWORD)

session = vk_api.VkApi(token=TOKEN_VK_USER)

@dataclass
class Database:
    # Названия таблиц
    tables_names = {'main_table': 'info_user',
                    'all_users': 'all_user',
                    'favorites_users': 'favorites_users',
                    'table_countries': 'list_countries'}


    def create_tables(self):
        with conn.cursor() as cur:
            cur.execute(f'''
                        CREATE TABLE IF NOT EXISTS {self.tables_names['table_countries']}(
                        id_country INT,
                        country VARCHAR(150)
                        );
                        ''')
            # =====================================================
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
            id INT not null generated always as identity primary key,
            profile_id INT,
            name VARCHAR(100),
            surname VARCHAR(100)
            );
            ''')
            # ==================================================
            cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tables_names['favorites_users']}(
            profile_id INT,
            name VARCHAR(100),
            surname VARCHAR(100),
            age INT
            );
            ''')
            conn.commit()
        conn.close()

    def drop_users(self):
        with conn.cursor() as cur:
            cur.execute(f'''
                        DROP TABLE {self.tables_names['all_users']} CASCADE;
                        ''')
            cur.execute(f'''
                        CREATE TABLE IF NOT EXISTS {self.tables_names['all_users']}(
                        id INT not null generated always as identity primary key,
                        profile_id INT,
                        name VARCHAR(100),
                        surname VARCHAR(100)
                        );
                        ''')
            conn.commit()
    def drop_tables(self):
        with conn.cursor() as cur:
            cur.execute(f'''
            DROP TABLE {self.tables_names['main_table']} CASCADE;
            DROP TABLE {self.tables_names['all_users']} CASCADE;
            DROP TABLE {self.tables_names['favorites_users']} CASCADE;
            DROP TABLE {self.tables_names['table_countries']} CASCADE;
            ''')
            conn.commit()
        conn.close()

    def write_id_country(self):

        id_countries = session.method('database.getCountries', {'need_all': 1,
                                                                       'count': 1000})
        with conn.cursor() as cur:
            for countries in id_countries['items']:
                if countries['title'] == "Кот-д'Ивуар":
                    continue
                cur.execute(f'''
    INSERT INTO list_countries(id_country, country)
    VALUES(
    {countries['id']}, {repr(countries['title'])}
    );
    ''')
                conn.commit()
            conn.close()


def user_db():
    test = Database()
    # test.drop_tables()
    # test.create_tables()
    # test.write_id_country()

user_db()

