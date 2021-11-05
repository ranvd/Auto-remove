'''
Blueprint 是一種可以組織程式的一個物件。例如我要做驗證，所有驗證的程式都可以綁在一個 Blueprint 裡面，
當需要驗證功能的時候直接呼叫 Blueprint
'''

from os import SEEK_CUR
import sys
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

# 建立 Blueprint 物件，名稱為 auth，從 __name__ 這裡來，/auth 為 URL。
# 並在 __init__.py 使用 app.register_blueprint() 將 blueprint 加入 app 中。
bp = Blueprint('auth', __name__, url_prefix='/auth')


'''
當使用者連接到 /register 底下，會依據使用者請求的方式決定要做的動作。
如果是 GET 就回傳預設的 HTML 網址，如果是 POST 就做 "註冊" 相關的動作。

- @bp.route()：定義 URL。但因為這是在 Blueprint 底下，因此他的 URL 會是 auth/register。
- request.method：看使用者 request 的方法。
- request.form：是一個特殊格式的 dict。
- db.execute：執行 SQL 指令，其中的 ? 符號，用來處理使用者的輸入資料，所以以下 SQL 指令可以理解成：
    INSERT INTO user (username, password) VALUES (username的值, generate_password_hash(password)的值)
- generate_password_hash：為了安全問題，永遠不要直接儲存密碼，因此這邊先將密碼做 hash 後再存入。
- db.commit()：當作完所有動作後，需要做 commit 動作確認這次的更動，否則資料庫是不會有更動的。
'''


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username,post_num, password) VALUES (?, ?, ?)",
                    (username, 0,generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # 如果註冊成功自動導向 auth.login 的 URL。註：url_for() 參數是 funtion 名稱。
                return redirect(url_for("auth.login"))
        # 儲存錯誤訊息，在 render 的時候可以用。
        flash(error)

    return render_template('auth/register.html')


'''
- fetchone() 這邊回傳一個資料而已，fetchall() 則是回傳所有的資料
- check_password_hash() 將資料做 hash 後與資料庫的做比對。
- session 是一個 dict 用來儲存 request 之間的資料，當認證成功後 user_id 會被儲存到 session 中，
    而認證資料會以 coockie 的方式傳回給使用者。使用者接下來的 request 就會以 coockie 當作認證。
'''


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            print(user['id'])
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


'''
- before_app_request(): 是指不管在任何的 request 下，都會先進下面這段 function。

下面這段 function 就是驗證 session 用的。
'''


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


'''
Logout 的時候需要將 session 清空。
'''


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
