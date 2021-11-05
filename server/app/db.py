'''
這個 applicatoin 使用 SQLite 當作 database 來儲存使用者資料。python 內建的 sqlite3 module 就資源 SQLite。

SQLite 是一個方便的使用的 database，不需要做過多的設定且內建於 python，但當同時有資料要寫入的時候，SQLite 會讓寫入的資料排隊，
這樣的特性在小資料的情況下不會察覺，如果有大量的資料需要使用的時候就會出現效能低落的問題。
'''

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

'''
- g 是一個特別的物件，對於每一個 request 都是獨立的，g 用來儲存 request 時許多不同的資料，像下面的 g.db 儲存的 database 的連線資料。這樣做的好處是，當在一個 request 需要用到兩次一樣的連線的時候，
就不會重複建立。
- current_app 是另一個特別物件，會指向 Flask app，可以在 request 中返回 app。
- sqlite3.connect() 用來與剛剛 current_app 指向的 DATABASE 做聯繫。
- sqlite3.Row() 告訴連線的 row 的格式。在這邊是 dict。
'''


def get_db():
    if 'db' not in g:
        print("IN GET_DB", current_app.config["DATABASE"])
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_COLNAMES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


'''
- open_resource() 打開一個檔案，只需要知道名字不需要知道在哪，只要這個檔案在 app 資料夾底下。
- get_db() 使用上面定義好的 funtion 建立與 database 的連線。
- click.command() 定義一個新的 command 叫做 init-db，裡面做 init_db()。

Command line Interface 相關資料：
https://flask.palletsprojects.com/en/2.0.x/cli/
'''


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


'''
app.teardown_appcontext() 最 return 前要做的事情，可以想像成 request 的事情做完後要做的事情，在這裡就是將 db 關起來。
app.cli.add_command() 增加新的指令讓 flask 可以呼叫
'''


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
