from bot_configs.token import TOKEN
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


session = vk_api.VkApi(token=TOKEN)

vk = session.get_api()

# переделал для кнопок
def send_message(user_id, message, keyboard=None):
    post = {'user_id': user_id,
            'message': message,
            'random_id': 0}

    if keyboard != None:
        post['keyboard'] = keyboard.get_keyboard()
    else:
        post = post

    session.method('messages.send', post)

def get_info_user(user_id):
    user_info = session.method('users.get', {'user_id': user_id,
                                             'fields': 'sex, bdate'}) # 1 - жен; 2 - муж; 0 - не указан
    print(user_info)
    for information in user_info:
        id_user = information['id'] # инфа
        bdate = information['bdate']
        sex = information['sex']
        name = information['first_name']
        surname = information['last_name']

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
            send_message(user_id, message='Привет! Я бот!')
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


