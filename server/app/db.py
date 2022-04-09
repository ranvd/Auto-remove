'''
db.py 處理 database 相關的功能
- 連線 db
- 關閉 db
- 初始化 db
'''


import sqlite3
import os
import click
from flask import current_app, g
from flask.cli import with_appcontext

'''
取得 database
'''
def get_db():
    if 'db' not in g:
        current_app.logger.info("Connecting to db")
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_COLNAMES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

'''
關閉 database
'''
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


'''
依據 schema.sql 檔案裡面的規定進行初始化 database
'''
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        db.commit()

'''
初始化 database
'''
def init_app(app):
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


'''
新增 init-db 指令
在 CLI 中輸入 flask init-db 即可初始化
'''
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo("Initialized the database.")

