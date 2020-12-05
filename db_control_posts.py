from pymongo import *

cluster = MongoClient('mongodb+srv://main_exterminated:******@cluster0.tj4ux.gcp.mongodb.net/posts_maindb'
                      '?retryWrites=true&w=majority')
cluster_users = MongoClient('mongodb+srv://main_exterminated:******@cluster0.tj4ux.gcp.mongodb.net/users_maindb'
                            '?retryWrites=true&w=majority')

users = cluster_users.users_maindb

posts = cluster.posts_maindb


def get_all_posts():
    response = [i for i in posts.main_col.find({})][::-1]
    for i in range(len(response)):
        response[i]['_id'] = ''
    return response


def get_last_id():
    if posts.main_col.find({}):
        id_list = []
        for dict in posts.main_col.find({}):
            for k, v in dict.items():
                if k == 'id':
                    id_list.append(v)
        if id_list:
            return int(id_list[-1])
        else:
            return 0
    return False


def get_all_names():
    if posts.main_col.find({}):
        name_list = []
        for dict in posts.main_col.find({}):
            for k, v in dict.items():
                if k == 'name':
                    name_list.append(v)
        if name_list:
            return name_list
    return False


def get_all_texts():
    if posts.main_col.find({}):
        text_list = []
        for dict in posts.main_col.find({}):
            for k, v in dict.items():
                if k == 'content':
                    text_list.append(v)
        if text_list:
            return text_list
    return False


def find_post_by_name(name):
    if posts.main_col.find_one({"name": name}):
        return posts.main_col.find_one({"name": name})
    else:
        return False


def find_post_by_id(id):
    if posts.main_col.find_one({"id": int(id)}):
        return posts.main_col.find_one({"id": int(id)})
    else:
        return False


def add_post(name, content, author):
    if get_all_names() and get_all_texts():
        if name in get_all_names() or content in get_all_texts():
            return 'Пост с таким содержанием или названием уже существует! Пожалуйста, смените их.'
    if not name or not content:
        return 'Содержание или название не указаны. Повторите попытку.'
    json = \
        {
            "author": author,
            "id": get_last_id() + 1,
            "name": name,
            "content": content,
            "comments": []
        }
    posts.main_col.insert_one(json)
    users.main_col.update({'id': author}, {'$push': {'posts': get_last_id()}})
    json['_id'] = ''
    return json


def delete_post_by_id(id):
    user_id = posts.main_col.find_one({"id": int(id)})['author']
    posts.main_col.delete_one({"id": int(id)})
    users.main_col.update({"id": user_id}, {'$pull': {'comments': {'post_id': int(id)}}})
    users.main_col.update({"id": user_id}, {"$pull": {'posts': int(id)}})


def add_comment(post_id, content, author):
    found_author = users.main_col.find_one({"id": int(author['id'])})
    found_author['_id'] = ''
    found_author['comments'] = []
    found_author['posts'] = []
    json = \
        {
            "author": found_author,
            "content": content,
            "post_id": int(post_id)
        }
    posts.main_col.update_many({"id": int(post_id)}, {'$push': {'comments': json}})
    users.main_col.update_many({"id": found_author['id']}, {'$push': {'comments': json}})
