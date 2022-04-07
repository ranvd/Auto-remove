import os
import sys
from flask import Flask, url_for, render_template
from flask_bootstrap import Bootstrap
import json

def create_app(Config_FileName = "config.json"):
    app = Flask(__name__, instance_relative_config=True)
    Bootstrap(app)

    try:
        app.config.from_file(Config_FileName, load=json.load)
    except:
        app.logger.error("Config file must be json format")
        sys.exit("Error occur")
    '''
    for conf in app.config:
        print(conf, " : ", app.config[conf])
    '''
    @app.route("/")
    def root():
        return render_template('base.html')

    @app.route("/sidebar")
    def sidebar():
        return render_template('album.html')

    @app.route("/album")
    def album():
        return render_template('sidebar.html')

    @app.route("/index")
    def index():
        return render_template('index.html', videos=[1,2,3,4,5,6,7,8,9,10], folders=["Folder1", "Folder2", "origin", "matting+styleTF"])

    

    return app

'''
if (__name__ == "__main__"):
    app = create_app()
'''