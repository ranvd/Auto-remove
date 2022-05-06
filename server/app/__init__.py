from operator import mod
import os
from pyexpat import model
import sys
from flask import Flask, url_for, render_template
from flask_bootstrap import Bootstrap
import json
import sqlite3
import multiprocessing
import sys


print(sys.argv)
# 這是 Flask 規定的函式名稱
def create_app(Config_FileName = None):
    '''
    建立整個完整的網站，裡面會呼叫 blueprint 與其他輔助 function。
    '''
    app = Flask(__name__, instance_relative_config=True)

    # try load configure from instance/config.py
    app.config.from_mapping(
        SECRET_KEY = "dev",
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
        QUEUE = os.path.join(app.instance_path, 'queue.sqlite'),
        UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    )
    if(Config_FileName):
        try:
          app.config.from_pyfile(Config_FileName, silent=True)
        except:
            app.logger.error("Config file must be py format")
            sys.exit("Error occur")

    '''
    for conf in app.config:
        print(conf, " : ", app.config[conf])
    '''

    # database 功能
    from . import db
    db.init_app(app)

    '''
    '''
    #json.dumps(dictionary, indent = 4)
    # Model 服務
    from . import model_process
    if 'run' in sys.argv:
        d = dict(app.config)
        with open('testing.json', 'w') as jsonfile:
            json.dump(d, jsonfile,default=str)
        model_line =  multiprocessing.Process(
            target=model_process.model_main_function,
            args=[app.config])

        model_line.start()
    
    # 登入登出與驗證功能
    from . import auth
    app.register_blueprint(auth.bp)

    from . import main_bp
    app.register_blueprint(main_bp.bp)
    app.add_url_rule('/', endpoint='main.index') 
    # 上面這行在這裡其實沒有意義，只是提醒index在main_bp裡
    
    

    @app.route("/newindex")
    def newindex():
        print(os.curdir)
        return os.getcwd()
    
    '''
    @app.route("/sibar")
    def sidebar():
        return render_template('album.html')

    @app.route("/album")
    def album():
        return render_template('sidebar.html')
    '''
    
    return app

'''
if (__name__ == "__main__"):
    app = create_app()
'''
