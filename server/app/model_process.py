
import sqlite3
from time import sleep


def model_main_function(*db_setting):
    queue = sqlite3.connect(
        db_setting[0],
        db_setting[1]
    )
    queue.row_factory = db_setting[2]
    
    print("START SUCESSFULLY")
    return