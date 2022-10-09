from database1 import test
import json
from datetime import datetime

year_now = datetime.now().year

requester = 22105995 # id пользователя бота
current_request = {   # параметры поиска
    'requester': requester,
    'age': 27,
    'gender': 'женский',
    'city': 'Москва',
    'country': 'Россия'
}

current_request_values = (
    current_request['requester'],
    current_request['age'],
    current_request['gender'],
    current_request['city'],
    current_request['country']
)
print(current_request_values)
print(type(current_request_values))
vk_data = [{'id': 403454198, 'bdate': '22.3.1997', 'first_name': 'Таня', 'last_name': 'Николаева', 'can_access_closed': True, 'is_closed': False}, {'id': 430467985, 'first_name': 'Варвара', 'last_name': 'Середнёва', 'can_access_closed': True, 'is_closed': False}, {'id': 496266400, 'first_name': 'Анастасия', 'last_name': 'Бессовская', 'can_access_closed': True, 'is_closed': True}, {'id': 496266300, 'first_name': 'Настя', 'last_name': 'Поповская', 'can_access_closed': True, 'is_closed': True}]
# with open('slist.txt', 'w') as file:
#     json.dump(vk_data, file, indent=2)
vk_data_fixed = []

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

photos = {'link': 'https://ya.ru/', 'likes': False}
photos_values = (photos['link'], photos['likes'])



# with open('slist.txt', 'r') as file:
#     data_dict = json.load(file)


for user in vk_data:
    if 'bdate' not in user:
        user['bdate'] = current_request['age']
    else:
        user['bdate'] = year_now - int(user['bdate'][-4:])
    del user['can_access_closed'], user['is_closed']
    user['user_age'] = user.pop('bdate')
    columns = ('id', 'first_name', 'last_name', 'user_age')
    columns_values = (user['id'], user['first_name'], user['last_name'], user['user_age'])
    vk_data_fixed.append(columns_values)


print(vk_data_fixed)

# наполняем базу
id_selection = test.insert_request('selection', current_request_values)

for user in vk_data_fixed:
    test.insert_base('preferences', 'users', 'photos', preferences_values, id_selection, user, photos_values)


# тест

test.change_favorites(requester, 430467985, True)
test.change_black_list(requester, 496266400, True)
test.change_viewed(requester, 403454198, True)
print(test.show_favorites(requester, False))
print(test.show_black_list(requester, False))
print(test.show_viewed(requester, False))
