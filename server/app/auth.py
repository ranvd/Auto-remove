'''
auth.py 處理所有有關驗證的工作
- 登入/登出
- session 處理。
- 註冊
'''
import os
import functools
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

'''
註冊
建立所有帳號基礎訊息，MAIN資料夾。
TODO: 下面註冊後直接跳向登入頁面，應該可以改成直接登入。
'''
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not confirm:
            error = 'Confirm is required.'
        elif password != confirm:
            error = 'Confirm mismatch'

        #print("this is error: ", error)
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, v_num, f_num) VALUES (?, ?, ?, ?)",
                    (username,generate_password_hash(password), 0, 1),
                )
                db.execute(
                    "INSERT INTO folder (f_name, author_id) VALUES (?,?)",
                    ("MAIN", username)
                )
                db.commit()

                # 建立使用者資料夾
                path = (current_app.config['UPLOAD_FOLDER'], username, "MAIN")
                os.makedirs(os.path.join(*path, "videos"))
                os.makedirs(os.path.join(*path, "backgrounds"))

            except Exception as Err:
                print(Err)
                error = f'User {username} is already registered.'
            else:
                return redirect(url_for("auth.login")) # 註冊完直接導向頁面
            
        flash(error)
    
    return render_template('auth/register.html')


'''
登入
註：
- flask 內建的 session 是 client side 的 session，server 不儲存使用者狀態。
'''
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username"
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'
        
        if error is None:
            session.clear()
            session['user_id'] = user['u_id'] # 這裡完全幫你處理好把 cookie 送到 client 的功能
            return redirect(url_for('main.index'))
        
        flash(error)
    return render_template('auth/login.html')


'''
登出
將 session 刪除。
'''
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


'''
condictional connection
在所有 request 進到任何 function 前先做 session 驗證。
'''
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    db = get_db()
    if user_id is None:
        g.user = None
    else:
        g.user = db.execute(
            'SELECT * FROM user WHERE u_id = ?', (user_id,)
        ).fetchone()

'''
要求使用者作任何事情前都需要登入
decorator
'''
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view