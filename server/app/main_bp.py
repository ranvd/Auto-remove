'''
網站所有主要功能
'''
import functools
from pickle import NONE
import queue
import random
import os
import time
from statistics import mode
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db, get_queue
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
        print(request.form)
        print(request.files)
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
            user_path = (current_app.config['UPLOAD_FOLDER'], g.user['username'])
            vsa_name = v_name[:-4] + str(time.time()) + v_name[-4:]
            bsa_name = b_name[:-4] + str(time.time()) + v_name[-4:]
            v_path = os.path.join(*user_path, "videos", vsa_name)
            b_path = os.path.join(*user_path, "backgrounds", bsa_name)

            # save data to folder
            video.save(v_path)
            background.save(b_path)

            db = get_db()
            db.execute(
                "INSERT INTO video (v_name, vsa_name, b_name, bsa_name, author_id)"
                "VALUES (?, ?, ?, ?, ?)",
                (v_name, vsa_name, b_name, bsa_name, g.user['u_id'])
            )
            db.commit()
    
    folder_list = GetUserFolder(g.user['u_id'])
    video_list = GetUserVideo(g.user['u_id'])
    return render_template('PCindex.html', folders=folder_list, videos=video_list, models=AI_MODEL)


@bp.route("/<string:name>/ceate_folder", methods=('GET', 'POST'))
@login_required
def create_new_folder(name):
    if(request.method == 'POST'):
        print(request.form)
        print(request.files['newBackground'])

        newBackground = request.files['newBackground']
        nB_name = newBackground.filename
        nBsa_name = nB_name[:-4] + str(time.time()) + nB_name[-4:]
        error = None

        if(not nB_name):
            error = "new Background is require"

        if (not error):
            user_path = (current_app.config['UPLOAD_FOLDER'], g.user['username'])
            nB_path = os.path.join(*user_path, "newBackground", nBsa_name)

            newBackground.save(nB_path)
            
            db = get_db()
            db.execute(
                "INSERT INTO newbackground (nb_name, nbsa_name, author_id)"
                "VALUES (?, ?, ?)",
                (nB_name, nBsa_name, g.user['u_id'])
            )
            db.commit()

    return redirect(url_for('main.profile', name=g.user['username']))


@bp.route("/<string:name>/moving_video", methods=("GET", "POST"))
@login_required
def moving_video(name):
    #TODO: 找b_name的方式應該可以優化

    if(request.method == "POST"):
        #current_app.logger.info("from moving_video: {}".format(request.form))
        vsa_name = request.form.getlist('select')
        Moving_folder = request.form['Move']
        '''
        '''
        # 依照v_name讀取database裡面相對應的b_name
        db = get_db()
        bsa_name = []
        for name in vsa_name:
            print(name)
            name = db.execute(
                "SELECT bsa_name FROM video"
                "WHERE author_id=(?) AND vsa_name=(?)",
                (g.user['username'], name)
            ).fetchone()['bsa_name']
            print("After: ", name)
            bsa_name.append(name)

        db.commit()

        # 將資料插到queue的database裡面
        queue = get_queue()
        for v_name, b_name in zip(vsa_name, bsa_name):
            v_path = (current_app.config['UPLOAD_FOLDER'], g.user['username'], "videos", v_name)
            b_path = (current_app.config['UPLOAD_FOLDER'], g.user['username'], "backgrounds", b_name)
            nb_path = (current_app.config['UPLOAD_FOLDER'], g.user['username'], "newBackground", Moving_folder)
            
            v_path = os.path.join(v_path)
            b_path = os.path.join(b_path)

            queue.execute(
                "INSERT INTO Queue (v_path, b_path, nb_path)"
                "VALUES (?, ?, ?)",
                (v_path, b_path, nb_path)
            )
        
        queue.commit()


        current_app.logger.info("FROM moving_video: {}".format((vsa_name)))
        current_app.logger.info("FROM moving_video: {}".format((Moving_folder)))

    return redirect(url_for('main.profile', name=g.user['username']))


@bp.route("/<string:name>/<string:folder>")
@login_required
def change_folder(name, folder):
    folder_list = GetUserFolder(g.user['u_id'])
    video_list = GetUserVideo(g.user['u_id'], folder)
    return render_template('PCindex.html', folders=folder_list, videos=video_list)


@bp.route("/<string:name>/<string:folder>")
@login_required
def folder(name, folder):
    current_app.logger.info('In folder function')
    return render_template('PCindex.html')


# ------------------ utils --------------------

def GetUserFolder(u_id):
    db = get_db()
    folder_list = db.execute(
            'SELECT nb_name, nbsa_name FROM newbackground WHERE author_id=?', (u_id,)
        ).fetchall()

    return [(dict(f)['nb_name'], dict(f)['nbsa_name']) for f in folder_list] # sqlite.Row 物件是一個 dict。

def GetUserVideo(u_id, f_id=None):
    db = get_db()
    if(f_id):
        video_list = db.execute("""
            SELECT v_name, vsa_name FROM video
            WHERE author_id=(?) AND nb_name=(?)
            """,
            (u_id,f_id)).fetchall()
    else:
        video_list = db.execute("""
            SELECT v_name, vsa_name FROM video
            WHERE author_id=(?) AND nb_name IS NULL
            """,
            (u_id,)).fetchall()

    return [(dict(v)['v_name'], dict(v)['vsa_name']) for v in video_list]
        

def AcceptedFile(*filename):
    return True