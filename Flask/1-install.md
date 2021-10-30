# Dependencies
以下這些 package 會在下載 Flask 的時候一並下載。
-   [Werkzeug](https://palletsprojects.com/p/werkzeug/) implements WSGI, the standard Python interface between applications and servers.
-   [Jinja](https://palletsprojects.com/p/jinja/) is a template language that renders the pages your application serves.
-   [MarkupSafe](https://palletsprojects.com/p/markupsafe/) comes with Jinja. It escapes untrusted input when rendering templates to avoid injection attacks.
-   [ItsDangerous](https://palletsprojects.com/p/itsdangerous/) securely signs data to ensure its integrity. This is used to protect Flask’s session cookie.
-   [Click](https://palletsprojects.com/p/click/) is a framework for writing command line applications. It provides the `flask` command and allows adding custom management commands.


# Virtual environment
## Create an environment
```command
$ mkdir myproject
$ cd myproject
$ python3 -m venv venv
```

## Activate the environment
```command
$ . venv/bin/activate
```

## Install Flask
```command
$ pip install Flask
```