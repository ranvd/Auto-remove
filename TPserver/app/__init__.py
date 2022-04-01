import os
from flask import Flask, url_for

'''
create_app() 是 app 建立函式，
- app = Flask(__name__, instance_relative_config=True)
    - __name__ 是當前 Python module 的名字，而 flask app 需要知道當前的檔案位置才能夠做相關路徑的設定，而 __name__ 是最快告訴她是誰的方法。
    - instance_relative_config=True 讓falsk app 可以用外面的設定檔(這個設定檔並不再 flask fodler)
- app.config.from_mapping() 就是剛剛提到的設定檔，from_mapping() 是其中一種載入方法
    - SECRET_KEY
    - DATABASE，instance folder 位置。
- app.config.from_pyfile() 將預設的設定依照輸入的檔名覆蓋，且這個檔案會在 instance 資料夾裡面
    - 這裡還有一個 test_config 是因為啟動一個 server 需要的設定檔案不見得一樣，因此這邊的邏輯就是如果沒有給定 test_config，就用預設的設定檔。
- os.makedirs() 是為了確保 app.instance_path 存在，因為 flask 不會自動建立資料夾，而且這個資料夾也是必須要，因為之後的 SQLite 資料會放在這裡。
- @app.route() 就是定義 URL 要回傳什麼資料，以下範例就是在 /hello URL 的時候回傳 Hello, World!。

'''
UPLOAD_FOLDER = '/home/minired/GraduationProject/Auto-remove/server/uploads'


def create_app(test_config=None):
    # create adn configure the app
    app = Flask(__name__, instance_relative_config=True)
    # 這邊是做設定，尤其是DATABASE 這個設定在之後會用到。
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        UPLOAD_FOLDER=UPLOAD_FOLDER
    )

    if test_config is None:
        # Load  the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def he():
        return 'Hello, World!'

    # print(app.config)
    # 在 db.py 建立過後後才加上的
    from . import db
    db.init_app(app)

    # 在 auth.py 建立過後才加上的
    from . import auth
    app.register_blueprint(auth.bp)

    '''
    - add_url_rule 基本上與 @app.route() 的意思是一樣的，endpoint是 view 與 function 連接的橋樑。
        也就是說如果 url_for() 這個函式裡面的值是放 endpoint，大部分的情況 endpoint 會與 funtion name 一樣。
        以下範例就代表當使用 url_for('index') 會到跟目錄。
    '''
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app


'''
if(__name__ == "__main__"):
    app = create_app()
    app.run()
'''
