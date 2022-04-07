import os
import sys
from flask import Flask, url_for, render_template
from flask_bootstrap import Bootstrap
import json

def create_app(Config_FileName = None):
    app = Flask(__name__, instance_relative_config=True)
    Bootstrap(app)

    # try load configure from instance/config.py
    app.config.from_mapping(
        SECRET_KEY = "dev",
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
        UPLOAD_FOLDER = "UPLOAD_FOLDER"
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

    from . import db
    db.init_app(app)



    @app.route("/")
    def index():
        return render_template('index.html', videos=[1,2,3,4,5,6,7,8,9,10], folders=["Folder1", "Folder2", "origin", "matting+styleTF"])
    
    @app.route("/sibar")
    def sidebar():
        return render_template('album.html')

    @app.route("/album")
    def album():
        return render_template('sidebar.html')


    return app

'''
if (__name__ == "__main__"):
    app = create_app()
'''