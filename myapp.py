from flask import Flask, render_template, redirect, request, flash, url_for, session, jsonify

import db_control as db
import db_control_posts as db_posts
import base64
import json


app = Flask(__name__, template_folder="templates")
app.secret_key = 'main_key'
app.config['UPLOAD_FOLDER'] = 'uploaded-avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/profile/<int:id>", methods=["GET", "POST"])
def profile(id):
    if 'user' not in session.keys():
        return redirect('/login')
    if request.method == 'POST':
        if len(request.form['status']) <= 180:
            if id == int(session['user']['id']) or 'admin' in session['user']['roles']:
                db.Other.change_status(id, request.form['status'])
    if int(id) in db.Show.show_all_ids():
        account = db.Other.find_user_by_id(int(id))
        if account:
            return render_template('index.html', account=account)
    return redirect('/posts')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            return render_template("login.html")
        login_successful = db.User.login_successful(username, password)
        if isinstance(login_successful, dict):
            try:
                session.pop('user')
            except KeyError:
                pass
            session_user = login_successful
            session_user['_id'] = ''
            for i in range(len(session_user['posts'])):
                if isinstance(session_user['posts'][i], dict):
                    try:
                        session_user['posts'][i]['_id'] = ''
                    except KeyError:
                        pass
            print(session_user)
            session['user'] = session_user
            return redirect('/profile/' + str(login_successful['id']))
        else:
            flash(login_successful)
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        avatar_hacker = open('./hacker.png', "rb")
        avatar = avatar_hacker.read()
        avatar_hacker.close()
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password-confirm']
        if not username or not password or not password_confirm:
            flash('Заполнены не все поля!')
            return render_template("sign_up.html")
        if password != password_confirm:
            flash('Пароли не совпадают!')
            return render_template("sign_up.html")
        # if request.files.get('file'):
        #     avatar = request.files.get('file').read()
        add_user = db.User.add_user_to_db(username, password, avatar)
        if isinstance(add_user, dict):
            add_user['_id'] = ''
            session['user'] = add_user
            return redirect('/profile/'+str(add_user['id']))
        else:
            flash(add_user)
    return render_template("sign_up.html")


@app.route('/posts', methods=["GET", "POST"])
def posts():
    if 'user' not in session.keys():
        return redirect('/login')
    posts = [i for i in db_posts.get_all_posts()]
    return render_template("post_page.html", posts=posts)


@app.route('/add_post', methods=["post"])
def _add_post():
    title = request.form['title']
    content = request.form['content']
    if 'user' not in session.keys():
        return redirect('/login')
    if not title or not content:
        posts = [i for i in db_posts.get_all_posts()]
        return redirect('/posts')
    add_post = db_posts.add_post(title, content, session['user'])
    if isinstance(add_post, dict):
        return redirect('/posts')
    else:
        flash(add_post)
    return redirect('/posts')


@app.route('/delete_post/<id>', methods=["get", "post"])
def delete_post(id):
    if 'user' not in session.keys():
        return redirect('/login')
    posts = [i for i in db_posts.get_all_posts()]
    needed_post = db_posts.find_post_by_id(int(id))
    if needed_post:
        if int(needed_post['author']['id']) == int(session['user']['id']) or 'admin' in session['user']['roles']:
            db_posts.delete_post_by_id(id)
            posts = [i for i in db_posts.get_all_posts()]
            return redirect(url_for("posts"))
    else:
        return redirect(url_for("posts"))


@app.route('/people', methods=["get"])
def people():
    if 'user' not in session.keys():
        return redirect('/login')
    users = db.Show.show_all_users()
    return render_template('people.html', users=users)


@app.route('/setstatus/<int:id>/<status>', methods=["POST"])
def setstatus(id, status):
    if 'user' not in session.keys():
        return redirect('/login')
    if id == int(session['user']['id']) or 'admin' in session['user']['roles']:
        db.Other.change_status(id, status)


@app.route('/view-post/<int:id>', methods=['GET', 'POST'])
def view_post(id):
    if 'user' not in session.keys():
        return redirect('/login')
    if not db_posts.find_post_by_id(id):
        return render_template('404.html'), 404
    if request.method == 'POST':
        text = request.form['text']
        if not text or len(text) > 180:
            return render_template('view_post.html', post=db_posts.find_post_by_id(id))
        db_posts.add_comment(id, text, session['user'])
    return render_template('view_post.html', post=db_posts.find_post_by_id(id))


@app.route('/logout')
def logout():
    try:
        session.pop('user')
        return redirect('/login')
    except KeyError:
        pass
    return redirect('/login')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/", methods=["GET", "POST"])
def default():
    return redirect('/login')


if __name__ == '__main__':
    app.run()
