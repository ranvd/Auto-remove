'''
網站所有主要功能
'''
import functools
import random
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db
from .auth import login_required

bp = Blueprint('main', __name__, url_prefix=None)

@bp.route("/")
def index():
    if (g.user):
        return redirect(url_for('main.profile', name=g.user['username']))
    
    return render_template('index.html')


@bp.route("/<string:name>")
@login_required
def profile(name):
    current_app.logger.info('In porfile function')
    folders = GetUserFolder(g.user['u_id'])
    videos = GetUserVideo(g.user['u_id'], random.randint(5,30))
    return render_template('index.html', folders=folders, videos=videos)


@bp.route("/<string:name>/<string:folder>")
@login_required
def folder(name, folder):
    current_app.logger.info('In folder function')
    return render_template('index.html')


# ------------------ utils --------------------

def GetUserFolder(u_id):
    db = get_db()
    return db.execute(
            'SELECT * FROM folder WHERE author_id = ?', (u_id,)
        ).fetchall()

def GetUserVideo(u_id, f_id):
    return [i for i in range(f_id)]