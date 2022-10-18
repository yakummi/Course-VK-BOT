import CourseVkBot.database.config
from CourseVkBot.bot_configs.token import TOKEN
import vk_api
import psycopg2
from CourseVkBot.bot_configs.token_user_vk import TOKEN_VK_USER
from vk_api.longpoll import VkLongPoll, VkEventType, VkMessageFlag
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import datetime
import json
from CourseVkBot.database.database import base
import sys

class VkBot:

    preferences = {
        'favorites': False,
        'black_list': False,
        'viewed': False
    }
    preferences_values = (
        preferences['favorites'],
        preferences['black_list'],
        preferences['viewed']
    )

    user_search_info = ['preferences', 'users', 'photos', preferences_values, ]

    gender_INFO = []

    photos_user = []

    user_information = []

    user_preferences = []

    i = 2

    session = vk_api.VkApi(token=TOKEN)

    vk = session.get_api()

    session_search = vk_api.VkApi(token=TOKEN_VK_USER)

    id_country = 0

    id_city_search = 0

    def get_photos_database(self, user_id):
        try:
            list_photo = []
            photos = self.session_search.method('photos.getAll', {'owner_id': user_id, 'extended': 1, 'count': 1})
            for photo in photos['items']:
                for new_photo in photo['sizes']:
                    if 'm' in new_photo['type']:
                        likes_ids = {'like': (photo['likes']['count']),
                                     'photo_id': (f'photo{str(user_id)}_' + str(photo['id']))}
                        if len(list_photo) < 1:
                            list_photo.append(likes_ids)
                        else:
                            break

                sorted(list_photo, key=lambda x: x['like'], reverse=True)
            for elements in list_photo:
                photos_tuple = (elements['photo_id'], elements['like'])
                self.photos_user.append(photos_tuple)
                return elements['photo_id'], elements['like']
        except Exception as ex:
            list_photo = []
            list_photo.append({'like': 0, 'photo_id': 'photo-216252230_457239173'})
            for elements in list_photo:
                photos_tuple = (elements['photo_id'], elements['like'])
                self.photos_user.append(photos_tuple)
                return elements['photo_id'], elements['like']

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

    def search_people(self, user_id, city, sex, country, age_from):
        search = self.session_search.method('users.search', {'sort': 0,
                                                             'city': city,
                                                             'sex': sex,
                                                             'count': 999,
                                                             'country': country,
                                                             'has_photo': 1,
                                                             'age_from': age_from-2,
                                                             'age_to': age_from+2})

        try:
            for info in search['items']:
                id_user = info['id']
                name = info['first_name']
                last_name = info['last_name']
                self.get_photos_database(id_user)

                test_info = []

                age = self.info_search(id_user, age_from)

                test_info.append(id_user)
                test_info.append(name)
                test_info.append(last_name)
                test_info.append(age)

                n = tuple(test_info)

                self.user_information.append(n)

                print(self.user_information)
                yield self.user_information

        except Exception as ex:
            print(ex)

    def get_info_user(self, user_id):
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

                    base.drop_tables()
                    base.create_tables()
                    base.write_id_country()


                    start_keyboard = VkKeyboard(one_time=False)
                    buttons = ['Старт']
                    buttons_colors = [VkKeyboardColor.POSITIVE]

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

                            self.user_preferences.append(country)

                            with conn.cursor() as cur:
                                try:
                                    select = f'''
                                           SELECT *
                                           FROM ids_countries
                                           where country = {repr(country)};
                                           '''
                                    cur.execute(select)
                                    rec = cur.fetchall()
                                    for id_c in rec:
                                        self.id_country += int(id_c[0])
                                    break
                                except Exception as ex:
                                    self.send_message(user_id, 'Вы ввели недопустимую страну, перезапустите бота!')
                                    sys.exit()

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
                            try:
                                city = str(event.text).capitalize() # Город
                                self.user_preferences.append(city)
                                self.get_id_cities(city, self.id_country)
                                break
                            except Exception as ex:
                                self.send_message(user_id, 'Вы ввели некорректный город, перезапустите бота.')
                                sys.exit()

                    new_keyboard = VkKeyboard(one_time=True)
                    button_name = ['Мужчины', 'Женщины']
                    button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        new_keyboard.add_button(btn, btn_color)

                    self.send_message(user_id, 'Дальше выберите кого нам искать.', new_keyboard, photo='photo-216252230_457239068')
                    for event in VkLongPoll(self.session).listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            gender = str(event.text).capitalize()
                            if gender == 'Мужчины':
                                self.gender_INFO.append(2)
                            elif gender == 'Женщины':
                                self.gender_INFO.append(1)

                            self.user_preferences.append(gender)
                            break

                    finish_tuple_info_user_preferences = tuple(self.user_preferences)

                    id_selection = base.insert_request('selection', finish_tuple_info_user_preferences)

                    self.user_search_info.append(id_selection)

                    self.send_message(user_id, 'Поиск начался...', photo=r'photo-216252230_457239019')
                    people = self.search_people(user_id, city=self.id_city_search, sex=int(self.gender_INFO[0]), country=self.id_country, age_from=self.user_preferences[1]) # остановился тут нужно понять как делать подбор анкет
                    try:
                        next(people)
                    except StopIteration as ex:
                        print(ex)
                    self.search_people(user_id, city=self.id_city_search, sex=int(self.gender_INFO[0]), country=self.id_country, age_from=self.user_preferences[1])

                    self.user_search_info.append(self.user_information)

                    print('Это из user_information: ', self.user_information)

                    photos_iter = (x for x in self.photos_user).__iter__()

                    print(photos_iter)

                    for users in self.user_information:
                        try:
                            base.insert_base('preferences', 'users', 'photos', self.preferences_values, id_selection,
                                            users,
                                            photos_iter.__next__())
                        except StopIteration:
                            print('Итератор опустошен')
                            break

                    questionnaires_keyboard = VkKeyboard(one_time=True)
                    button_name = ['Показать анкеты']
                    button_color = [VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        questionnaires_keyboard.add_button(btn, btn_color)

                    self.send_message(user_id, 'Нажмите "показать анкеты", чтобы увидеть анкеты.', keyboard=questionnaires_keyboard)

                if text == 'показать анкеты':
                    keyboard_user = VkKeyboard(one_time=False)
                    button_name = ['Следующий пользователь', 'В избранное', 'Избранные']
                    button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        keyboard_user.add_button(btn, btn_color)
                    keyboard_user.add_line()
                    keyboard_user.add_button(label='Добавить в черный список', color=VkKeyboardColor.NEGATIVE)

                    conn = psycopg2.connect(database=CourseVkBot.database.config.Settings.DATABASE,
                                            user=CourseVkBot.database.config.Settings.USER,
                                            password=CourseVkBot.database.config.Settings.PASSWORD)
                    with conn.cursor() as cur:
                        select_user = f'''
                        SELECT *
                        FROM users
                        limit 1; '''
                        cur.execute(select_user)
                        rec = cur.fetchall()
                        for elements in rec:
                            name = elements[1]
                            surname = elements[2]
                            id = elements[0]
                            list = {'id': id,
                                    'name': name,
                                    'surname': surname}

                        with open('data/user_search.json', 'w', encoding='utf-8') as f:
                            json.dump(list, f, indent=4, ensure_ascii=False)

                    with open('data/user_search.json', 'r', encoding='utf-8') as f:
                        user = json.load(f)



                    photos = self.get_photos_database(user['id'])
                    # photo = self.get_photos_database(photos_iter.__next__())

                    self.send_message(user_id, f"Имя: {user['name']}\nФамилия: {user['surname']}\nВозраст: {self.info_search(int(user['id']), 18)}\nСсылка: {'https://vk.com/id'+str(user['id'])}", keyboard_user, photo=photos[0])
                    base.change_viewed(user_id, user['id'], False)

                if text == 'следующий пользователь':
                    self.search_people(user_id, city=self.id_city_search, sex=int(self.gender_INFO[0]), country=self.id_country, age_from=self.user_preferences[1]) # остановился тут нужно понять как делать подбор анкет
                    self.user_search_info.append(self.user_information)

                    photos_iter = (x for x in self.photos_user).__iter__()

                    print(photos_iter)

                    for users in self.user_information:
                        try:
                            base.insert_base('preferences', 'users', 'photos', self.preferences_values, id_selection,
                                             users,
                                             photos_iter.__next__())
                        except StopIteration:
                            print('Итератор опустошен')
                            break

                    global i
                    conn = psycopg2.connect(database=CourseVkBot.database.config.Settings.DATABASE,
                                            user=CourseVkBot.database.config.Settings.USER,
                                            password=CourseVkBot.database.config.Settings.PASSWORD)
                    with conn.cursor() as cur:
                        keyboard_user = VkKeyboard(one_time=True)
                        button_name = ['Следующий пользователь', 'В избранное', 'Избранные']
                        button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE,
                                        VkKeyboardColor.POSITIVE]
                        for btn, btn_color in zip(button_name, button_color):
                            keyboard_user.add_button(btn, btn_color)

                        keyboard_user.add_line()
                        keyboard_user.add_button(label='Добавить в черный список', color=VkKeyboardColor.NEGATIVE)
                        select_user = f'''
                                        SELECT *
                                        FROM users
                                        where id_preferences = {self.i};
                                        '''
                        cur.execute(select_user)
                        rec = cur.fetchall()
                        for elements in rec:
                            name = elements[1]
                            surname = elements[2]
                            id = elements[0]
                            list = {'id': id,
                                    'name': name,
                                    'surname': surname}

                        with open('data/user_search.json', 'w', encoding='utf-8') as f:
                            json.dump(list, f, indent=4, ensure_ascii=False)

                    with open('data/user_search.json', 'r', encoding='utf-8') as f:
                        user = json.load(f)

                    # photos = self.get_photos_database(user['id'])



                    n = next(people)
                    print(n)

                    photo = self.get_photos_database(int(n[-1][0]))
                    print(photo)

                    list = {
                            "id": n[-1][0],
                            "name": n[-1][1],
                            "surname": n[-1][2]
                        }

                    with open('data/user_search.json', 'w', encoding='utf-8') as f:
                        json.dump(list, f, indent=4, ensure_ascii=False)

                    base.insert_base('preferences', 'users', 'photos', self.preferences_values, id_selection,
                                     n[-1],
                                     photo)

                    self.send_message(user_id, f"Имя: {n[-1][1]}\nФамилия: {n[-1][2]}\nВозраст: {int(n[-1][3])}\nСсылка: {'https://vk.com/id'+str(n[-1][0])}", keyboard_user, photo=photo[0])

                    next(people)

                    self.i += 1
                    base.change_viewed(user_id, user['id'], True)

                if text == 'в избранное':

                    keyboard_user = VkKeyboard(one_time=True)
                    button_name = ['Следующий пользователь', 'В избранное', 'Избранные']
                    button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE,
                                    VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        keyboard_user.add_button(btn, btn_color)

                    keyboard_user.add_line()
                    keyboard_user.add_button(label='Добавить в черный список', color=VkKeyboardColor.NEGATIVE)

                    with open('data/user_search.json', 'r', encoding='utf-8') as f:
                        user = json.load(f)

                    base.change_favorites(user_id, user['id'], True)
                    self.send_message(user_id, 'Пользователь добавлен в избранный лист', keyboard_user)

                if text == 'избранные':

                    keyboard_user = VkKeyboard(one_time=True)
                    button_name = ['Следующий пользователь', 'В избранное', 'Избранные']
                    button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE,
                                    VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE]

                    for btn, btn_color in zip(button_name, button_color):
                        keyboard_user.add_button(btn, btn_color)

                    keyboard_user.add_line()
                    keyboard_user.add_button(label='Добавить в черный список', color=VkKeyboardColor.NEGATIVE)

                    favorites_users = base.show_favorites(user_id, True)
                    print(favorites_users)
                    try:
                        for x in favorites_users:
                            self.send_message(user_id, f"Имя: {x[0]}\nФамилия: {x[1]}\nСсылка: {'https://vk.com/id' + str(x[4])}\nВозраст: {x[2]}", keyboard_user)

                    except Exception as ex:
                        self.send_message(user_id, "У вас нет избранных.", keyboard_user)

                if text == 'добавить в черный список':

                    keyboard_user = VkKeyboard(one_time=True)
                    button_name = ['Следующий пользователь', 'В избранное', 'Избранные']
                    button_color = [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE,
                                    VkKeyboardColor.POSITIVE]
                    for btn, btn_color in zip(button_name, button_color):
                        keyboard_user.add_button(btn, btn_color)

                    keyboard_user.add_line()
                    keyboard_user.add_button(label='Добавить в черный список', color=VkKeyboardColor.NEGATIVE)

                    with open('data/user_search.json', 'r', encoding='utf-8') as f:
                        user = json.load(f)

                    base.change_black_list(user_id, user['id'], True)

                    self.send_message(user_id, f'{user["name"]} добавлен в черный список.', keyboard=keyboard_user)


if __name__ == '__main__':
    test = VkBot()
    
    test.bot_functionality()