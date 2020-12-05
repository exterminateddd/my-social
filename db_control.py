import hashlib

from pymongo import MongoClient
from PIL import Image, ImageDraw
from flask import url_for


cluster = MongoClient('mongodb+srv://main_exterminated:secret_key@cluster0.tj4ux.gcp.mongodb.net/users_maindb?retryWrites=true&w=majority')

db = cluster.users_maindb


def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


class Username:
    @staticmethod
    def check_if_username_is_occupied(username: str):
        if db.main_col.find_one({"username": username}):
            return True
        return False

    @staticmethod
    def find_user_by_username(username: str):
        if db.main_col.find_one({"username": username}):
            return db.main_col.find_one({"username": username})
        return False


class Show:
    @staticmethod
    def show_all_users():
        if db.main_col.find():
            return [i for i in db.main_col.find({})]
        return False

    @staticmethod
    def show_all_usernames():
        if db.main_col.find():
            return [i['username'] for i in db.main_col.find()]
        return False

    @staticmethod
    def show_all_ids():
        if db.main_col.find({}):
            return [i['id'] for i in db.main_col.find()]
        return False


class Other:
    @staticmethod
    def return_last_id():
        if Show.show_all_ids():
            return Show.show_all_ids()[-1]
        return False

    @staticmethod
    def find_user_by_id(id: int):
        for user in Show.show_all_users():
            if int(user['id']) == id:
                return user
        return False

    @staticmethod
    def change_username(id: int, username: str):
        if db.main_col.find_one({"id": id}):
            db.main_col.update_one({
                'id': id
            }, {
                '$set': {
                    'username': username
                }
            })

    @staticmethod
    def change_status(id: int, status: str):
        print(db.main_col.find_one({"id": id}))
        if db.main_col.find_one({"id": id}):
            db.main_col.update_one({
                'id': id
            }, {
                '$set': {
                    'status': status
                }
            })
            return True
        else:
            return False


class User:
    @staticmethod
    def add_user_to_db(username: str, password: str, avatar):
        if username in Show.show_all_usernames():
            return 'Имя пользователя занято!'
        if len(password) < 8:
            return 'Пароль недостаточно длинный!'
        img = Image.new('RGB', (640, 480), (255, 255, 255))
        print(url_for('static', filename='avatars/' + str(Other.return_last_id() + 1) + '.jpg'))
        # img.save(url_for('static', filename='avatars/'+str(Other.return_last_id()+1)+'.jpg'))
        img.save("./static/avatars/"+str(Other.return_last_id()+1)+'.jpg')
        with open("./static/avatars/"+str(Other.return_last_id()+1)+'.jpg', 'wb') as f:
            f.write(avatar)
        final_dict = {
            "id": Other.return_last_id()+1,
            "username": username,
            "password": encrypt_string(password),
            "roles": ['user'],
            "status": 'Пусто',
            "posts": [],
            "comments": []
        }
        db.main_col.insert_one(final_dict)
        return Show.show_all_users()[-1]

    @staticmethod
    def login_successful(username: str, password: str):
        for user in Show.show_all_users():
            if user['username'] == username and user['password'] == encrypt_string(password):
                user_r = user
                return user_r
        return 'Неверное имя пользователя или пароль!'
