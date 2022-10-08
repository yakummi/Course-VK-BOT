import CourseVkBot.database.config
from CourseVkBot.bot_configs.token import TOKEN
import vk_api
import psycopg2
from CourseVkBot.bot_configs.token_user_vk import TOKEN_VK_USER
from vk_api.longpoll import VkLongPoll, VkEventType, VkMessageFlag
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import datetime
import json
from CourseVkBot.database.database import Database
from CourseVkBot.database.database1 import base



class VkBot:

    user_preferences = []

    i = 1

    session = vk_api.VkApi(token=TOKEN)

    vk = session.get_api()

    session_search = vk_api.VkApi(token=TOKEN_VK_USER)

    id_country = 0

    id_city_search = 0


    def get_photos(self, user_id):
        try:
            list_photo = []
            photos = self.session_search.method('photos.getAll', {'owner_id': user_id, 'extended': 1, 'count': 3})
            print(photos)
            for e in photos['items']:
                list_photo.append('photo'+str(e['owner_id'])+'_'+str(e['id']))
            return list_photo
        except Exception as ex:
            pass

    def info_search(self, user_id, age_user):
        info = self.session_search.method('users.get', {'user_id': user_id,
                                                        'fields': 'bdate'})
        for i in info:
            if 'bdate' in i.keys():
                date = i['bdate'].split('.')
                if len(date) == 3:
                    year_now = datetime.datetime.now().year
                    return int(year_now) - int(date[2])
                else:
                    return age_user
            else:
                return age_user

    def get_id_cities(self, q, id_country):
        id_city = self.session_search.method('database.getCities', {'q': q,
                                                                    'country_id': id_country})

        for i in id_city['items']:
            if i['title'] == q:
                self.id_city_search+=i['id']

    def send_message(self, user_id, message, keyboard=None, photo=None):
        post = {'user_id': user_id,
                'message': message,
                'random_id': 0,
                'attachment': photo}

        if keyboard != None:
            post['keyboard'] = keyboard.get_keyboard()
        else:
            post = post

        self.session.method('messages.send', post)

    def search_people(self, user_id, city, sex, country, age_from, stop=None):
        conn = psycopg2.connect(database=CourseVkBot.database.config.Settings.DATABASE, user=CourseVkBot.database.config.Settings.USER,
                                password=CourseVkBot.database.config.Settings.PASSWORD)
        search = self.session_search.method('users.search', {'sort': 0,
                                                             'city': city,
                                                             'sex': sex,
                                                             'count': 999,
                                                             'country': country,
                                                             'has_photo': 1,
                                                             'age_from': age_from-2,
                                                             'age_to': age_from+2})

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
                        # Добавляем пользователей в базу данных
                except Exception as ex:
                    print(ex)
                conn.close()

    def get_info_user(self, user_id): # не нужна
        info = {}
        user_info = self.session.method('users.get', {'user_id': user_id,
                                                      'fields': 'sex, bdate'})
        for information in user_info:
            id_user = information['id']
            bdate = information['bdate']
            year_now = datetime.datetime.now().year
            bdate = int(year_now) - int(bdate.split('.')[2])
            sex = information['sex']
            name = information['first_name']
            surname = information['last_name']
            info[id_user] = {'age': bdate,
                             'sex': sex,
                             'name': name,
                             'surname': surname}


    def bot_functionality(self):
        for event in VkLongPoll(self.session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()
                user_id = event.user_id


                if text == '/start':
                    self.user_preferences.append(user_id)

                    drop_table = Database()
                    drop_table.drop_users()
                    start_keyboard = VkKeyboard(one_time=False)
                    buttons = ['Старт']
                    buttons_colors = [VkKeyboardColor.POSITIVE]
                    #
                    for btn, btn_color in zip(buttons, buttons_colors):
                        start_keyboard.add_button(btn, btn_color)
                    self.send_message(user_id, message='Привет, я Бот, который найдет тебе нового друга в твоем городе!\nСледуй инструкциям, чтобы я смог понять тебя и твои пожелания!', keyboard=start_keyboard, photo=r'photo-216252230_457239018')
                    self.get_info_user(user_id)

                if text == 'старт':
                    keyboard = VkKeyboard(one_time=True)

                    buttons = ['Указать возраст поиска']
                    buttons_colors = [VkKeyboardColor.PRIMARY]
                    for btn, btn_color in zip(buttons, buttons_colors):
                        keyboard.add_button(btn, btn_color)

                    self.send_message(user_id, 'Чтобы начать поиск, нам необходимо собрать с вас некую информацию. Следуйте кнопкам снизу.', keyboard)

                if text == 'указать возраст поиска':
                    self.send_message(user_id, 'Введите людей с каким возрастом мы ищем')
                    for event in VkLongPoll(self.session).listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            self.user_preferences.append(int(event.text))
                            break

                    keyboard_country = VkKeyboard(one_time=True)
                    button_city = ['Указать страну']
                    button_color_city = [VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_city, button_color_city):
                        keyboard_country.add_button(btn, btn_color)

                    self.send_message(user_id, 'Отлично, двигаемся дальше.', keyboard=keyboard_country)

                if text == "указать страну":
                    self.send_message(user_id, 'Введите название вашей страны.')
                    for event in VkLongPoll(self.session).listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            conn = psycopg2.connect(database=CourseVkBot.database.config.Settings.DATABASE, user=CourseVkBot.database.config.Settings.USER,
                                                    password=CourseVkBot.database.config.Settings.PASSWORD)

                            country = str(event.text).capitalize()
                            with open('data/data_country.txt', 'w', encoding='utf-8') as f: # переделать в бд потом
                                f.write(str(country))

                            self.user_preferences.append(country)

                            with conn.cursor() as cur:
                                select = f'''
                                            SELECT *
                                            FROM list_countries
                                            where country = {repr(country)};
                                            '''
                                cur.execute(select)
                                rec = cur.fetchall()
                                for id_c in rec:
                                    self.id_country+=int(id_c[0])

                            break

                    keyboard_city = VkKeyboard(one_time=True)
                    button_city = ['Указать город']
                    button_color_city = [VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_city, button_color_city):
                        keyboard_city.add_button(btn, btn_color)

                    self.send_message(user_id, 'Отлично', keyboard=keyboard_city)

                if text == 'указать город':
                    self.send_message(user_id, 'Введите ваш город.')
                    for event in VkLongPoll(self.session).listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            # try:
                            city = str(event.text).capitalize() # Город
                            with open('data/data_city.txt', 'w', encoding='utf-8') as f: # потом сделать в бд
                                f.write(str(city))
                            self.user_preferences.append(city)

                            self.get_id_cities(city, self.id_country)
                            print(self.id_country)
                            print(self.id_city_search)
                            break
                            # except NameError as ex:
                            #     print(ex)



                    new_keyboard = VkKeyboard(one_time=True)
                    button_name = ['Мужчины', 'Женщины']
                    button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        new_keyboard.add_button(btn, btn_color)

                    self.send_message(user_id, 'Дальше выберите кого нам искать.', new_keyboard, photo='photo-216252230_457239068')
                    for event in VkLongPoll(self.session).listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            gender = str(event.text).capitalize()  # Пол
                            self.user_preferences.append(gender)

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

                    print(self.user_preferences)

                    finish_tuple_info_user_preferences = tuple(self.user_preferences)

                    base.insert_request('selection', finish_tuple_info_user_preferences)

                    self.send_message(user_id, 'Поиск начался...', photo=r'photo-216252230_457239019')
                    self.search_people(user_id, city=self.id_city_search, sex=int(sex), country=self.id_country, age_from=self.user_preferences[1], stop=not None) # остановился тут нужно понять как делать подбор анкет


                    ankets_keyboard = VkKeyboard(one_time=True)
                    button_name = ['Показать анкеты']
                    button_color = [VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        ankets_keyboard.add_button(btn, btn_color)

                    self.send_message(user_id, 'Нажмите "показать анкеты", чтобы увидеть анкеты.', keyboard=ankets_keyboard)

                if text == 'показать анкеты':
                    keyboard_user = VkKeyboard(one_time=True)
                    button_name = ['Следующий пользователь', 'В избранное', 'Избранные', 'Информация о поиске']
                    button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        keyboard_user.add_button(btn, btn_color)

                    conn = psycopg2.connect(database=CourseVkBot.database.config.Settings.DATABASE,
                                            user=CourseVkBot.database.config.Settings.USER,
                                            password=CourseVkBot.database.config.Settings.PASSWORD)
                    with conn.cursor() as cur:
                        select_user = f'''
                        SELECT *
                        FROM all_user
                        limit 1;
                        '''
                        cur.execute(select_user)
                        rec = cur.fetchall()
                        for elements in rec:
                            name = elements[2]
                            surname = elements[3]
                            id = elements[1]
                            list = {'id': id,
                                    'name': name,
                                    'surname': surname}
                        with open('data/user_search.json', 'w', encoding='utf-8') as f:
                            json.dump(list, f, indent=4, ensure_ascii=False)

                    with open('data/user_search.json', 'r', encoding='utf-8') as f:
                        user = json.load(f)

                    photos = self.get_photos(user['id'])
                    # info_search(int(user['id']), 18) # Брать из бд у нашего пользователя
                    self.send_message(user_id, f"Имя: {user['name']}\nФамилия: {user['surname']}\nВозраст: {self.info_search(int(user['id']), 18)}\nСсылка: {'https://vk.com/id'+str(user['id'])}", keyboard_user, photo=photos)

                if text == 'следующий пользователь':
                    global i
                    conn = psycopg2.connect(database=CourseVkBot.database.config.Settings.DATABASE,
                                            user=CourseVkBot.database.config.Settings.USER,
                                            password=CourseVkBot.database.config.Settings.PASSWORD)
                    with conn.cursor() as cur:
                        keyboard_user = VkKeyboard(one_time=True)
                        button_name = ['Следующий пользователь', 'В избранное', 'Избранные', 'Информация о поиске']
                        button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE,
                                        VkKeyboardColor.POSITIVE]
                        for btn, btn_color in zip(button_name, button_color):
                            keyboard_user.add_button(btn, btn_color)
                        select_user = f'''
                                        SELECT *
                                        FROM all_user
                                        where id = {self.i};
                                        '''
                        cur.execute(select_user)
                        rec = cur.fetchall()
                        for elements in rec:
                            name = elements[2]
                            surname = elements[3]
                            id = elements[1]
                            list = {'id': id,
                                    'name': name,
                                    'surname': surname}
                        with open('data/user_search.json', 'w', encoding='utf-8') as f:
                            json.dump(list, f, indent=4, ensure_ascii=False)

                    with open('data/user_search.json', 'r', encoding='utf-8') as f:
                        user = json.load(f)

                    photos = self.get_photos(user['id'])

                    self.send_message(user_id, f"Имя: {user['name']}\nФамилия: {user['surname']}\nВозраст: {self.info_search(int(user['id']), 18)}\nСсылка: {'https://vk.com/id'+str(user['id'])}", keyboard_user, photo=photos)
                    self.i = self.i + 1

                if text == 'в избранное':
                    conn = psycopg2.connect(database=CourseVkBot.database.config.Settings.DATABASE,
                                            user=CourseVkBot.database.config.Settings.USER,
                                            password=CourseVkBot.database.config.Settings.PASSWORD)

                    keyboard_user = VkKeyboard(one_time=True)
                    button_name = ['Следующий пользователь', 'В избранное', 'Избранные', 'Информация о поиске']
                    button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE,
                                    VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        keyboard_user.add_button(btn, btn_color)

                    with open('data/user_search.json', 'r', encoding='utf-8') as f:
                        user = json.load(f)

                    with conn.cursor() as cur:
                        cur.execute(f'''
                        INSERT INTO favorites_users(profile_id, name, surname, age)
                        VALUES(
                        {(user['id'])}, {repr(user['name'])}, {repr(user['surname'])}, {self.info_search(int(user['id']), 18)}
                        );
    ''')
                        conn.commit()


                    self.send_message(user_id, 'Пользователь добавлен в избранный лист', keyboard_user)

                if text == 'избранные':
                    conn = psycopg2.connect(database=CourseVkBot.database.config.Settings.DATABASE,
                                            user=CourseVkBot.database.config.Settings.USER,
                                            password=CourseVkBot.database.config.Settings.PASSWORD)

                    keyboard_user = VkKeyboard(one_time=True)
                    button_name = ['Следующий пользователь', 'В избранное', 'Избранные', 'Информация о поиске']
                    button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE,
                                    VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        keyboard_user.add_button(btn, btn_color)

                    with conn.cursor() as cur:
                        with conn.cursor() as cur:
                            select = f'''
                                        SELECT *
                                        FROM favorites_users;
                                        '''
                            cur.execute(select)
                            rec = cur.fetchall()
                            print(rec)
                            for e in rec:
                                self.send_message(user_id, f"Имя: {e[1]}\nФамилия: {e[2]}\nСсылка: {'https://vk.com/id' + str(e[0])}\nВозраст: {self.info_search(int(user['id']), 18)}", keyboard_user)
                            if rec == []:
                                self.send_message(user_id,"У вас нет избранных.", keyboard_user)

                if text == 'информация о поиске':

                    info_keyboard = VkKeyboard(one_time=True)
                    button_name = ['Следующий пользователь', 'В избранное', 'Избранные', 'Информация о поиске']
                    button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE,
                                    VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        info_keyboard.add_button(btn, btn_color)

                    with open('data/data_sex.txt') as f: # потом сделать в бд
                        sex = f.read()
                    with open('data/data_city.txt', encoding='utf-8') as f:
                        city = f.read()
                    with open('data/data_country.txt', encoding='utf-8') as f:
                        country = f.read()

                    self.send_message(user_id, f'Информация:\nСтрана: {country}\nГород: {city}\nПол: {sex}', keyboard=info_keyboard)



if __name__ == '__main__':
    test = VkBot()
    test.bot_functionality()