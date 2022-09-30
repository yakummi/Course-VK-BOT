from bot_configs.token import TOKEN
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

session = vk_api.VkApi(token=TOKEN)

vk = session.get_api()

def send_message(user_id, message):
    session.method('messages.send', {'user_id': user_id,
                                     'message': message,
                                     'random_id': 0})

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

for event in VkLongPoll(session).listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text.lower()
        user_id = event.user_id

        if text == '/start':
            send_message(user_id, message='Привет! Я бот!')
            get_info_user(user_id)
