#! /bin/bash
export FLASK_ENV=development
flask init-db
flask run

rm -r uploads
