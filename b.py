from ctypes import sizeof
import threading
from time import sleep

def do_something():
    print("Start Sleeping")
    sleep(1)
    print("End Sleeping")


threads = []

for _ in range(10):
    t = threading.Thread(target=do_something)
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()

print("TESTING")


