import time
import threading
import random

def foo():
    wait_time=25+random.uniform(0,10)
    print(wait_time)
    print(time.ctime())
    threading.Timer(wait_time, foo).start()

foo()
