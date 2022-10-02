import database.config
from bot_configs.token import TOKEN
import vk_api
import psycopg2
from bot_configs.token_user_vk import TOKEN_VK_USER
from vk_api.longpoll import VkLongPoll, VkEventType, VkMessageFlag
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import datetime
import random

session = vk_api.VkApi(token=TOKEN)

vk = session.get_api()

session_search = vk_api.VkApi(token=TOKEN_VK_USER)

random_len = 0

id_country = 0

id_city_search = 0

def get_id_cities(q, id_country):
    global id_city_search
    id_city = session_search.method('database.getCities', {'q': q,
                                                           'country_id': id_country})

    for i in id_city['items']:
        if i['title'] == q:
            id_city_search+=i['id']

get_id_cities('Москва', 1)

# get_id_cities('Владивосток', 1)
# переделал для кнопок
def send_message(user_id, message, keyboard=None, photo=None):
    post = {'user_id': user_id,
            'message': message,
            'random_id': 0,
            'attachment':photo}

    if keyboard != None:
        post['keyboard'] = keyboard.get_keyboard()
    else:
        post = post

    session.method('messages.send', post)

def search_people(user_id, city, sex, country, stop=None): # доработать функция стадия test # update test работает
    conn = psycopg2.connect(database=database.config.Settings.DATABASE, user=database.config.Settings.USER,
                            password=database.config.Settings.PASSWORD)
    search = session_search.method('users.search', {'sort': 0, # sort - 0 по популярности
                                             'city': city,
                                             'sex': sex,
                                            'count': 999,
                                                    'country': country})

    if stop != None:
        with conn.cursor() as cur:
            try:
                for info in search['items']:
                    id_user = info['id']
                    name = info['first_name']
                    last_name = info['last_name']
                    cur.execute(f'''
    INSERT INTO all_user(profile_id, name, surname)
    VALUES(
    {id_user}, {repr(name)}, {repr(last_name)}
    );
    ''')
                    conn.commit()
            except Exception as ex:
                print(ex)
            conn.close()

# search_people(37, 2, stop=True)
# search_people(37, 2, stop=True)

# search_people('Москва', 2) # Такой метод работает, с ним и будем контактировать

def get_info_user(user_id):
    info = {}
    user_info = session.method('users.get', {'user_id': user_id,
                                             'fields': 'sex, bdate'}) # 1 - жен; 2 - муж; 0 - не указан
    print(user_info)
    for information in user_info:
        id_user = information['id'] # инфа
        bdate = information['bdate']
        year_now = datetime.datetime.now().year
        bdate = int(year_now) - int(bdate.split('.')[2]) # получил возраст пользователя
        sex = information['sex']
        name = information['first_name']
        surname = information['last_name']
        info[id_user] = {'age': bdate,
                         'sex': sex,
                         'name': name,
                         'surname': surname}

def test1():
    for event in VkLongPoll(session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text.lower()
            user_id = event.user_id

            if text == '/start':
                start_keyboard = VkKeyboard(one_time=False)
                buttons = ['Старт']
                buttons_colors = [VkKeyboardColor.POSITIVE]
                #
                for btn, btn_color in zip(buttons, buttons_colors):
                    start_keyboard.add_button(btn, btn_color)
                send_message(user_id, message='Привет, я Бот, который найдет тебе нового друга в твоем городе!\nСледуй инструкциям, чтобы я смог понять тебя и твои пожелания!', keyboard=start_keyboard, photo=r'photo-216252230_457239018')
                get_info_user(user_id)

            # стадия теста
            # здесь мы у пользователя просим указать город, после чего его сообщение должно добавиться в базу данных
            if text == 'старт':
                keyboard = VkKeyboard(one_time=True)
                # keyboard.add_button('Указать город', VkKeyboardColor.POSITIVE)

                buttons = ['Указать страну']
                buttons_colors = [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.SECONDARY, VkKeyboardColor.NEGATIVE]
                #
                for btn, btn_color in zip(buttons, buttons_colors):
                    keyboard.add_button(btn, btn_color)

                send_message(user_id, 'Чтобы начать поиск, нам необходимо собрать с вас некую информацию. Следуйте кнопкам снизу.', keyboard)

            # проверку на пользователя
            if text == "указать страну": # РАЗОБРАТЬСЯ С ПОЛУЧЕНИЕМ СООБЩЕНИЙ ОТ ПОЛЬЗОВАТЕЛЯ
                send_message(user_id, 'Введите название вашей страны.')
                for event in VkLongPoll(session).listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        conn = psycopg2.connect(database=database.config.Settings.DATABASE, user=database.config.Settings.USER,
                                                password=database.config.Settings.PASSWORD)

                        # city = str(event.text).capitalize()  # Город
                        # with open('data/data_city.txt.txt', 'w', encoding='utf-8') as f:
                        #     f.write(str(city))
                        country = str(event.text).capitalize()

                        with conn.cursor() as cur:
                            select = f'''
                                        SELECT *
                                        FROM list_countries
                                        where country = {repr(country)};
                                        '''
                            cur.execute(select)
                            rec = cur.fetchall()
                            for id_c in rec:
                                global id_country
                                id_country+=int(id_c[0])

                        break

                keyboard_city = VkKeyboard(one_time=True)
                button_city = ['Указать город']
                button_color_city = [VkKeyboardColor.POSITIVE]
                for btn, btn_color in zip(button_city, button_color_city):
                    keyboard_city.add_button(btn, btn_color)

                send_message(user_id, 'Отлично', keyboard=keyboard_city)
            if text == 'указать город':
                send_message(user_id, 'Введите ваш город.')
                for event in VkLongPoll(session).listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        city = str(event.text).capitalize() # Город
                        get_id_cities(city, id_country)
                        print(id_country)
                        print(id_city_search)
                        break


                new_keyboard = VkKeyboard(one_time=True)
                button_name = ['Мужчины', 'Женщины']
                button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE]
                for btn, btn_color in zip(button_name, button_color):
                    new_keyboard.add_button(btn, btn_color)

                send_message(user_id, 'Дальше выберите кого нам искать.', new_keyboard)
                for event in VkLongPoll(session).listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        gender = str(event.text).capitalize()  # Пол
                        if gender == 'Мужчины':
                            sex = 2
                            with open('data/data_sex.txt', 'w', encoding='utf-8') as f:
                                f.write(str(sex))

                        else:
                            sex = 1
                            with open('data/data_sex.txt', 'w', encoding='utf-8') as f:
                                f.write(str(sex))

                        break


                with open('data/data_sex.txt', 'r', encoding='utf-8') as f:
                    sex = f.read()

                send_message(user_id, 'Поиск начался...', photo=r'photo-216252230_457239019')
                search_people(user_id, city=id_city_search, sex=int(sex), country=id_country, stop=not None) # остановился тут нужно понять как делать подбор анкет


                skip_keyboard = VkKeyboard(one_time=True)
                button_name = ['Скип']
                button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE]
                for btn, btn_color in zip(button_name, button_color):
                    skip_keyboard.add_button(btn, btn_color)

                conn = psycopg2.connect(database=database.config.Settings.DATABASE, user=database.config.Settings.USER,
                                        password=database.config.Settings.PASSWORD)

                with conn.cursor() as cur:
                    select_len = f'''
                                                            SELECT COUNT(name)
                                                            FROM all_user;
                                                            '''
                    cur.execute(select_len)
                    rec = cur.fetchall()
                    for l in rec:
                        global random_len
                        random_len+=int(l[0])


                send_message(user_id, 'Нажмите скип, чтобы увидеть анкеты.', keyboard=skip_keyboard)

            if text == 'скип':
                skip_keyboard = VkKeyboard(one_time=True)
                button_name = ['Скип']
                button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE]
                for btn, btn_color in zip(button_name, button_color):
                    skip_keyboard.add_button(btn, btn_color)

                rand = random.randint(1, random_len)
                conn = psycopg2.connect(database=database.config.Settings.DATABASE, user=database.config.Settings.USER,
                                        password=database.config.Settings.PASSWORD)
                with conn.cursor() as cur:
                    select_user = f'''
                                SELECT *
                                FROM all_user
                                where id = {rand};
                                '''
                    cur.execute(select_user)
                    rec = cur.fetchall()

                    send_message(user_id, rec, keyboard=skip_keyboard)

                # while True:
                #     send_message(user_id, 'Ну как вам?', skip_keyboard)
                #     conn = psycopg2.connect(database=database.config.Settings.DATABASE,
                #                             user=database.config.Settings.USER,
                #                             password=database.config.Settings.PASSWORD)
                #
                #     with conn.cursor() as cur:
                #         try:
                #             select = f'''
                #                                                 SELECT *
                #                                                 FROM all_users;
                #                                                 '''
                #             cur.execute(select)
                #             rec = cur.fetchall()
                #             send_message(user_id, rec)
                #             break
                #         except Exception as ex:
                #             pass







                # search_people(city, sex)  берем с базы данных

                    # my_id = session.method('messages.getHistory', {'user_id': user_id, 'count': 1})
                    # response = event.text.lower()
                    # print(response)

                # get_message(user_id)
                # доработать "получить сообщение пользователя на кнопку"

            # проверка на наличие города у пользователя в database
        # if text == 'начать поиск':
        #     pass
                    # пользуемся https://dev.vk.com/method/users.search

test1()
