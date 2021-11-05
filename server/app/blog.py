import os
import sys
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from app.auth import login_required
from app.db import get_db

'''
不像 auth.py 裡面的 Blueprint，這個 Blueprint 沒有 url_prefix。因此網址就是直接接到設定的網址上。
'''
bp = Blueprint('blog', __name__)


'''
這個 index 會給出最近po 的貼文，且會依照使用者的 id，讓使用者編輯自己的貼文
'''


@bp.route('/')
def index():
    posts = ""
    if(g.user):
        return redirect(url_for("blog.profile", name=g.user['username']))

    return render_template('blog/index.html', posts=posts)


@bp.route('/<name>')
def profile(name):
    if(g.user):
        db = get_db()
        posts = db.execute(
            'SELECT p.id, title, created, author_id, username, filename'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.author_id = ?'
            ' ORDER BY created DESC',
            (g.user['id'],)
        ).fetchall()

    return render_template('blog/index.html', posts=posts)


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/<string:name>/create', methods=('GET', 'POST'))
@login_required
def create(name):
    if request.method == 'POST':
        # 檢查有沒有路徑可以放資料
        try:
            os.makedirs(os.path.join(
                current_app.config["UPLOAD_FOLDER"], name))
        except OSError:
            pass

        title = request.form['title']
        file = request.files['file']
        error = None

        if not title:
            error = 'Title is required.'
        if not file.filename:
            error = 'No selected file.'

        if error is not None:
            flash(error)
        else:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(
                    current_app.config['UPLOAD_FOLDER'], name, filename))

            db = get_db()
            db.execute(
                'INSERT INTO post (title, author_id, filename)'
                ' VALUES (?, ?, ?)',
                (title, g.user['id'], file.filename)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# return the user's file back to user


@bp.route('/<string:name>/<filename>')
def downloadfile(name, filename):
    print(os.path.join(current_app.config["UPLOAD_FOLDER"], name, filename))
    return send_from_directory(os.path.join(current_app.config["UPLOAD_FOLDER"], name), filename)


'''
- about 用來丟出 exception。*(HTTPS 協定裏面的)
'''


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, filename, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?'
                ' WHERE id = ?',
                (title, id)
            )
            db.commit()
            print("?here")
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    os.remove(os.path.join(
        current_app.config["UPLOAD_FOLDER"], post["username"], post["filename"]))
    return redirect(url_for('blog.index'))
