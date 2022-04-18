import sqlite3

db = sqlite3.connect('flaskr.sqlite')

cur = db.cursor()
folders = cur.execute("""
SELECT * FROM folder
""").fetchall()

videos = cur.execute(
    "SELECT * FROM video"
).fetchall()

user = cur.execute(
    "SELECT * FROM user"
).fetchall()


cur.close()
print("USER:")
for u in user:
    print(u)

print("VIDEOS:")
for v in videos:
    print(v)

print("FOLDER:")
for f in folders:
    print(f)