import datetime
import requests
# from pprint import pprint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from data_base import *

offset = 0


def get_token():
    token = ''
    return token


def get_tokenvk():
    tokenvk = ''
    return tokenvk


class Vkbot:
    def __init__(self):
        self.authorize = vk_api.VkApi(token=get_token())
        self.longpoll = VkLongPoll(self.authorize)

    def write_message(self, sender, message):
        self.authorize.method('messages.send', {'user_id': sender,
                                                'message': message,
                                                'random_id': get_random_id()})

    def seeker_name(self, user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': get_token(),
                  'user_ids': user_id,
                  'v': '5.131'}
        resp = requests.get(url, params)
        response = resp.json()
        information_dict = response['response']
        for i in information_dict:
            for key, value in i.items():
                first_name = i.get('first_name')
                return first_name

    def get_seekers_sex(self, user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': get_token(), 'user_ids': user_id,
                  'fields': 'sex', 'v': '5.131'}
        resp = requests.get(url, params=params)
        response = resp.json()
        information_list = response['response']
        for i in information_list:
            if i.get('sex') == 2:
                sex_found = 1
                return sex_found
            elif i.get('sex') == 1:
                sex_found = 2
                return sex_found

    def get_city_by_name(self, user_id, city_name):
        url = f'https://api.vk.com/method/database.getCities'
        params = {'access_token': get_token(), 'q': f'{city_name}',
                  'need_all': 0, 'count': 1000, 'v': '5.131'}
        resp = requests.get(url, params=params)
        response = resp.json()
        information_list = response['response']
        list_cities = information_list['items']
        for i in list_cities:
            found_city_name = i.get('title')
            if found_city_name == city_name:
                found_city_id = i.get('id')
                return int(found_city_id)

    def get_city_by_user(self, user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': get_token(), 'fields': 'city',
                  'user_ids': user_id, 'v': '5.131'}
        resp = requests.get(url, params=params)
        response = resp.json()
        information_cities = response['response']
        for i in information_cities:
            if 'city' in i:
                city = i.get('city')
                id = str(city.get('id'))
                return id
            elif 'city' not in i:
                self.write_message(user_id, 'Введите свой город, пожалуйста!')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        city_name = event.text
                        id_city = self.get_city_by_name(user_id, city_name)
                        if id_city != '' or id_city != None:
                            return str(id_city)

    def age_from(self, user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': get_token(), 'user_ids': user_id,
                  'fields': 'bdate', 'v': '5.131'}
        resp = requests.get(url, params=params)
        response = resp.json()
        information = response['response']
        for i in information:
            b_date = i.get('bdate')
        date_list = b_date.split('.')
        if len(date_list) == 3:
            year = int(date_list[2])
            actual_year = int(datetime.date.today().year)
            age = actual_year - year
            return age    
        elif len(date_list) == 2 or b_date not in information:
            self.write_message(user_id, 'Возраст кандидатов, начиная от ...')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    return age

    def age_to(self, user_id):
        self.write_message(user_id, 'Возраст кандидатов до...')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                age = event.text
                return age

    def find_candidate(self, user_id):
        url = 'https://api.vk.com/method/users.search'

        age_from = int(self.age_from(user_id))
        age_to = age_from + 1
        '''метод age_to работает не правильно'''
        print(f'{age_from} up {age_to}')


        params = {'access_token': get_tokenvk(), 'v': '5.131', 'sex': self.get_seekers_sex(user_id),
                  'age_from': age_from, 'age_to': age_to,
                  'city': self.get_city_by_user(user_id), 'relation': '6',
                  'fields': 'is_closed, id, first_name, last_name', 'count': 100}
        res = requests.get(url, params=params)
        resp_json = res.json()
        print(resp_json)
        resp_dict = resp_json['response']
        resp_list = resp_dict['items']
        for person in resp_list:
            if person.get('is_closed') == False:
                first_name = person.get('first_name')
                last_name = person.get('last_name')
                vk_id = str(person.get('id'))
                vk_link = 'vk.com/id' + str(person.get('id'))
                insert_data_found_users(first_name, last_name, vk_id, vk_link)
            else:
                continue
            return f'Есть результаты поиска!'

    def get_fotos_id(self, user_id):
        url = f'https://api.vk.com/method/photos.getProfile'
        params = {'access_token': get_tokenvk(), 'v': '5.131', 'type': 'album',
                  'person_id': 'user_id', 'extended': 1, 'count': 30
                  }
        resp = requests.get(url, params=params)
        dict_fotos = dict()
        resp_json = resp.json()
        dict_1 = resp_json['response']
        list_1 = dict_1['items']
        for i in list_1:
            foto_id = str(i.get('id'))
            i_likes = i.get('likes')
            if i_likes.get('count'):
                dict_fotos['likes'] = foto_id
        list_of_ids = sorted(dict_fotos.items(), reverse=True)
        return list_of_ids

    def get_foto_1(self, user_id):
        list = self.get_fotos_id(user_id)
        count = 0
        for i in list:
            count += 1
            if count == 1:
                return i[1]

    def get_foto_2(self, user_id):
        list = self.get_fotos_id(user_id)
        count = 0
        for i in list:
            count += 1
            if count == 2:
                return i[1]

    def get_foto_3(self, user_id):
        list = self.get_fotos_id(user_id)
        count = 0
        for i in list:
            count += 1
            if count == 3:
                return i[1]

    def send_foto_1(self, user_id, message, offset):
        self.authorize.method('messages.send', {'user_id': user_id,
                                                'access_token': get_tokenvk(), 'message': message,
                                                'attachment':
                                                    f'photo{self.object_id()(offset)}_{self.get_foto_1(self.object_id()(offset))}',
                                                'random_id': 0})

    def send_foto_2(self, user_id, message, offset):
        self.authorize.method('messages.send', {'user_id': user_id,
                                                'access_token': get_tokenvk(), 'message': message,
                                                'attachment':
                                                    f'photo{self.object_id(offset)}_{self.get_foto_2(self.object_id(offset))}',
                                                'random_id': 0})

    def send_foto_3(self, user_id, message, offset):
        self.authorize.method('messages.send', {'user_id': user_id,
                                                'access_token': get_tokenvk(), 'message': message,
                                                'attachment':
                                                    f'photo{self.object_id(offset)}_{self.get_foto_3(self.object_id(offset))}',
                                                'random_id': 0})

    def object_id(self, offset):
        tuple_object = select_unseen(offset)
        list_object = []
        for i in tuple_object:
            list_object.append(i)
        return list_object[2]

    def found_object_info(self, offset):
        tuple_object = select_unseen(offset)
        list_object = []
        for i in tuple_object:
            list_object.append(i)
        return f'{list_object[0]} {list_object[1]}, {list_object[3]}'

    def find_object(self, user_id, offset):
        self.write_message(user_id, self.found_object_info(offset))
        self.object_id(offset)
        insert_data_seen_users(self.object_id(offset), offset)
        self.get_fotos_id(self.object_id(offset))
        self.send_foto_1(user_id, 'First photo', offset)
        if self.get_foto_2(self.object_id(offset)) != None:
            self.send_foto_2(user_id, 'Second photo', offset)
            self.send_foto_3(user_id, 'Third photo', offset)
        else:
            self.write_message(user_id, 'No more photos')


bot = Vkbot()

