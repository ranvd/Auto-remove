#! /bin/bash
export FLASK_ENV=development
flask init-db
flask run --host 0.0.0.0
rm -r uploads appconfig.json
