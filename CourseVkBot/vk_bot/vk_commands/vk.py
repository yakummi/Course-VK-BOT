from CourseVkBot.bot_configs.token_user_vk import TOKEN_VK_USER
import vk_api

class Vk:
    session_search = vk_api.VkApi(token=TOKEN_VK_USER)

    def get_photos_database(self, user_id, photos_user):
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
                photos_user.append(photos_tuple)
                return elements['photo_id'], elements['like']
        except Exception as ex:
            list_photo = []
            list_photo.append({'like': 0, 'photo_id': 'photo-216252230_457239173'})
            for elements in list_photo:
                photos_tuple = (elements['photo_id'], elements['like'])
                photos_user.append(photos_tuple)
                return elements['photo_id'], elements['like']

vk_com = Vk()