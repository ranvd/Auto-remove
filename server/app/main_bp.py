'''
網站所有主要功能
'''
from crypt import methods
import functools
from os import getuid
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db

bp = Blueprint('main', __name__, url_prefix=None)

@bp.route("/")
def index():
    if (g.user):
        return redirect(url_for('main.profile', name=g.user['username']))
    
    return render_template('index.html')

@bp.route("/<string:name>")
def profile():
    return render_template('index.html')
# ------------------ utils --------------------

def GetUserFolder(u_id):
    db = get_db()
    return db.execute(
            'SELECT * FROM folder WHERE author_id = ?', (u_id,)
        ).fetchall()

def GetUserVideo():
    return