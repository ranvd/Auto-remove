import sqlite3

db = sqlite3.connect('flaskr.sqlite')

cur = db.cursor()
folders = cur.execute("""
SELECT * FROM newbackground
""").fetchall()

videos = cur.execute(
    "SELECT * FROM video"
).fetchall()

user = cur.execute(
    "SELECT * FROM user"
).fetchall()

w = cur.execute(
    """SELECT * FROM video
    WHERE bsa_name=(?)""",
    ("com (1)1650728976.4051828.mp4",)
).fetchall()
'''
'''
queue = sqlite3.connect('queue.sqlite')
cur = queue.cursor()

Q = cur.execute(
    "SELECT * FROM Queue"
).fetchall()



for ww in w:
    print(ww)

print("USER:")
for u in user:
    print(u)

print("VIDEOS:")
for v in videos:
    print(v)

print("FOLDER:")
for f in folders:
    print(f)

'''
'''
print("QUEUE")
for q in Q:
    print(q)

cur.close()