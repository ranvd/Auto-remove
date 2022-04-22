'''
網站所有主要功能
'''
import functools
import random
import os
import time
from statistics import mode
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db
from .auth import login_required

bp = Blueprint('main', __name__, url_prefix=None)
AI_MODEL = ['Matting', 'StyleTransfer']


@bp.route("/")
def index():
    if (g.user):
        return redirect(url_for('main.profile', name=g.user['username']))
    
    return render_template('index.html')


@bp.route("/<string:name>", methods=('GET', 'POST'))
@login_required
def profile(name):
    if( request.method == "POST"):
        # 處理使用者上傳資料
        #print(request.form)
        error = None
        video = request.files['video']
        background = request.files['background']
        v_name = video.filename
        b_name = background.filename

        if(not v_name or not b_name):
            error = "Require both background and video."
        elif(not AcceptedFile(v_name, b_name)):
            error = "File type incorrect."
        
        if(not error):
            user_path = (current_app.config['UPLOAD_FOLDER'], g.user['username'], "MAIN")
            vsa_name = v_name+str(time.time())
            bsa_name = b_name+str(time.time())
            v_path = os.path.join(*user_path, "videos", vsa_name)
            b_path = os.path.join(*user_path, "backgrounds", bsa_name)
            video.save(v_path)
            background.save(b_path)

            db = get_db()
            db.execute(
                "INSERT INTO video (v_name, vsa_name, b_name, bsa_name, author_id, folder_name)"
                "VALUES (?, ?, ?, ?, ?, ?)",
                (v_name, vsa_name, b_name, vsa_name, g.user['u_id'], "MAIN")
            )
            db.commit()
    
    folder_list = GetUserFolder(g.user['u_id'])
    folder_list = [dict(f)['f_name'] for f in folder_list] # sqlite.Row 物件是一個 dict。

    video_list = GetUserVideo(g.user['u_id'])
    video_list = [(dict(v)['v_name'], dict(v)['vsa_name']) for v in video_list]
    return render_template('PCindex.html', folders=folder_list, videos=video_list, models=AI_MODEL)


@bp.route("/<string:name>/ceate_folder", methods=('GET', 'POST'))
@login_required
def create_new_folder(name):
    if(request.method == 'POST'):
        filename = None
        for model in AI_MODEL:
            try:
                request.form[model] == 'on'
                if (filename):
                    filename += model
                else:
                    filename = model
            except:
                continue

        #print(filename)
        if(filename):
            db = get_db()
            db.execute(
                "INSERT INTO folder(f_name, author_id) VALUES (?, ?)",
                (filename, g.user['u_id'])
            )
            f_num = db.execute(
                "SELECT f_num FROM user WHERE u_id=(?)",
                (g.user['u_id'],)
            ).fetchone()
            f_num = dict(f_num)['f_num'] + 1

            db.execute(
                "UPDATE user SET f_num=(?)"
                "WHERE u_id=(?)",
                (f_num, g.user['u_id'])
            )

            db.commit()

    return redirect(url_for('main.profile', name=g.user['username']))


@bp.route("/<string:name>/moving_video", methods=("GET", "POST"))
@login_required
def moving_video(name):
    current_app.logger.info("from moving_video: {}".format(request.form))
    Selected_video = request.form.getlist('select')
    Moving_folder = request.form['Move']

    current_app.logger.info("FROM moving_video: {}".format(Selected_video))
    current_app.logger.info("FROM moving_video: {}".format(Moving_folder))
    return redirect(url_for('main.profile', name=g.user['username']))


@bp.route("/<string:name>/<string:folder>")
@login_required
def change_folder(name, folder):
    folder_list = GetUserFolder(g.user['u_id'])
    folder_list = [dict(f)['f_name'] for f in folder_list] # sqlite.Row 物件是一個 dict。
    
    video_list = GetUserVideo(g.user['u_id'], folder)
    video_list = [dict(v)['v_name'] for v in video_list]
    return render_template('PCindex.html', folders=folder_list, videos=video_list)


@bp.route("/<string:name>/<string:folder>")
@login_required
def folder(name, folder):
    current_app.logger.info('In folder function')
    return render_template('PCindex.html')


# ------------------ utils --------------------

def GetUserFolder(u_id):
    db = get_db()
    return db.execute(
            'SELECT f_name FROM folder WHERE author_id=?', (u_id,)
        ).fetchall()

def GetUserVideo(u_id, f_id="MAIN"):
    # TODO: 要增加folder轉換之間的條件
    db = get_db()
    return db.execute("""
        SELECT v_name, vsa_name FROM video
        WHERE author_id=(?) AND folder_name=(?)
        """,
        (u_id, f_id)).fetchall()

def AcceptedFile(*filename):
    return True