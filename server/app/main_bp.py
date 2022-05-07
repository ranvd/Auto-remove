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
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for, send_from_directory
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db, get_queue
from .auth import login_required

bp = Blueprint('main', __name__, url_prefix=None)
User_Option = ['styletransfer', 'people']
Option_Val = {
    'styletransfer' : 1,
    'people' : 2
}


@bp.route("/")
def index():
    if (g.user):
        return redirect(url_for('main.profile', name=g.user['username']))
    
    return render_template('index.html')


@bp.route("/<string:name>", methods=('GET', 'POST'))
@login_required
def profile(name):
    #print(request.method)
    if( request.method == "POST"):
        # 處理使用者上傳資料
        #print(request.form)
        #print(request.files)
        error = None
        video = request.files['video']
        background = request.files['background']
        v_name = video.filename
        b_name = background.filename

        if(not v_name or not b_name):
            error = "Require both background and video."
        elif(not AcceptedFile(v_name, b_name)):
            print("file type error")
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
        
        #flash(error)

        # 其實我不太清楚這裏面的原理，但這樣做可以防止input file tag的值還存在檔案裏面
        return redirect(url_for('main.profile', name=g.user['username']))
    
    folder_list = GetUserFolder(g.user['u_id'])
    video_list = GetUserVideo(g.user['u_id'])
    return render_template('PCindex.html', folders=folder_list, videos=video_list)


@bp.route("/<string:name>/ceate_folder", methods=('GET', 'POST'))
@login_required
def create_new_folder(name):
    if(request.method == 'POST'):
        opt_val = 0
        for opt in User_Option:
            if(request.form[opt] == 'True'):
                opt_val += Option_Val[opt]

        current_app.logger.info(request.files['newBackground'])

        newBackground = request.files['newBackground']
        nB_name = newBackground.filename
        nBsa_name = nB_name[:-4] + str(time.time()) + nB_name[-4:]
        error = None

        if(not nB_name):
            error = "new Background is require"
        elif (not AcceptedFile(nB_name)):
            print("file type error")
            error = "File type incorrect"

        if (not error):
            user_path = (current_app.config['UPLOAD_FOLDER'], g.user['username'])
            nB_path = os.path.join(*user_path, "newBackground", nBsa_name)

            newBackground.save(nB_path)
            
            db = get_db()
            db.execute(
                "INSERT INTO newbackground (nb_name, nbsa_name, author_id, opt)"
                "VALUES (?, ?, ?, ?)",
                (nB_name, nBsa_name, g.user['u_id'], opt_val)
            )
            db.commit()

        #flash(error)

    return redirect(url_for('main.profile', name=g.user['username']))


@bp.route("/<string:name>/moving_video", methods=("GET", "POST"))
@login_required
def moving_video(name):
    #TODO: 找b_name的方式應該可以優化
    if(request.method == "POST"):
        vsa_name_list = request.form.getlist('select')
        nbsa_name = request.form['Move']
        '''
        '''
        # 依照v_name讀取database裡面相對應的b_name
        db = get_db()
        bsa_name_list = []
        v_name_list = []
        for name in vsa_name_list:
            row_info = db.execute(
                """SELECT * FROM video
                WHERE author_id=(?) AND vsa_name=(?)""",
                (g.user['u_id'], name)
            ).fetchone()
            bsa_name_list.append(row_info['bsa_name'])
            v_name_list.append(row_info['v_name'])

        opt_val = db.execute(
            """SELECT opt FROM newbackground
            WHERE nbsa_name=(?)
            """,
            (nbsa_name,)
        ).fetchone()
        opt_val = opt_val['opt']

        current_app.logger.info(bsa_name_list)
        db.commit()

        # 將資料插到queue的database裡面
        queue = get_queue()
        for v_name, vsa_name, bsa_name in zip(v_name_list, vsa_name_list, bsa_name_list):
            vsa_path = (current_app.config['UPLOAD_FOLDER'], g.user['username'], "videos", vsa_name)
            bsa_path = (current_app.config['UPLOAD_FOLDER'], g.user['username'], "backgrounds", bsa_name)
            nbsa_path = (current_app.config['UPLOAD_FOLDER'], g.user['username'], "newBackground", nbsa_name)
            
            vsa_path = os.path.join(*vsa_path)
            bsa_path = os.path.join(*bsa_path)
            nbsa_path = os.path.join(*nbsa_path)
            
            current_app.logger.info(vsa_path)
            current_app.logger.info(bsa_path)
            queue.execute(
                """INSERT INTO Queue (author, author_id, v_name, v_path, b_path, nb_path, opt)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (g.user['username'], g.user['u_id'], v_name, vsa_path, bsa_path, nbsa_path, opt_val)
            )
        
        queue.commit()


        current_app.logger.info("FROM moving_video: {}".format((vsa_name_list)))
        current_app.logger.info("FROM moving_video: {}".format((nbsa_name)))

    return redirect(url_for('main.profile', name=g.user['username']))


@bp.route("/<string:name>/<string:folder>")
@login_required
def change_folder(name, folder):
    print("change folder")
    folder_list = GetUserFolder(g.user['u_id'])
    video_list = GetUserVideo(g.user['u_id'], folder)
    return render_template('PCfolder.html', folders=folder_list, videos=video_list)

@bp.route("/download/<string:name>/<string:video>")
@login_required
def download_video(name, video):
    print('download')
    path = (current_app.config["UPLOAD_FOLDER"], g.user['username'], "videos")
    return send_from_directory(os.path.join(*path), video, as_attachment=True)

# ------------------ utils --------------------

def GetUserFolder(u_id):
    db = get_db()
    folder_list = db.execute(
            'SELECT nb_name, nbsa_name FROM newbackground WHERE author_id=?', (u_id,)
        ).fetchall()

    return [(dict(f)['nb_name'], dict(f)['nbsa_name']) for f in folder_list] # sqlite.Row 物件是一個 dict。

def GetUserVideo(u_id, f_id=None): # f_id 是 nb_name 但 nb_name 對應的是實際的 nb_name
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
    accepted = ['mp4', 'avi', 'png', 'jpg']
    for file in filename:
        print(file[-3:])
        if(file[-3:] not in accepted):
            return False
    return True