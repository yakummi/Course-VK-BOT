from bot_configs.token import TOKEN
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import datetime

session = vk_api.VkApi(token=TOKEN)

vk = session.get_api()

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

def search_people(city, sex): # доработать функция стадия test
    search = session.method('users.search', {'sort': 0, # sort - 0 по популярности
                                             'hometown': city,
                                             'sex': sex})
    print(search)


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

# доработка - получить последнее сообщение пользователя
def get_message(user_id):
    text = session.method('messages.getHistory', {'user_id': user_id,
                                           'count': 1})

    print(text)

for event in VkLongPoll(session).listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text.lower()
        user_id = event.user_id

        if text == '/start':
            send_message(user_id, message='Привет, я Бот, который найдет тебе нового друга в твоем городе!\nСледуй инструкциям, чтобы я смог понять тебя и твои пожелания!', photo=r'photo-216252230_457239018')
            get_info_user(user_id)

        # стадия теста
        # здесь мы у пользователя просим указать город, после чего его сообщение должно добавиться в базу данных
        if text == '/test':
            keyboard = VkKeyboard(one_time=False)
            keyboard.add_location_button()
            keyboard.add_line()
            # keyboard.add_button('Указать город', VkKeyboardColor.POSITIVE)

            buttons = ['Указать город']
            buttons_colors = [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.SECONDARY, VkKeyboardColor.NEGATIVE]
            #
            for btn, btn_color in zip(buttons, buttons_colors):
                keyboard.add_button(btn, btn_color)

            send_message(user_id, 'Чтобы начать поиск, нам необходимо собрать с вас некую информацию. Введите ваш город.', keyboard)

            if text == "указать город":
                send_message(user_id, 'Введите название вашего города.')
                text = text
                get_message(user_id)
                # доработать "получить сообщение пользователя на кнопку"

            # проверка на наличие города у пользователя в database
                if text == 'начать поиск':
                    pass
                    # пользуемся https://dev.vk.com/method/users.search