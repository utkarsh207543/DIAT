import sys
import math
import random
import threading
import time

def ex_th(i):

    print("Thread {} sleeps at {}".format(i,time.strftime("%H:%M:%d", time.gmtime())))

    rand_sleep_time = random.randint(1,5)
    time.sleep(rand_sleep_time)

    print("Thread {} stops sleeping at {}".format(i,time.strftime("%H:%M:%d", time.gmtime())))

for i in range(1000):
    thread = threading.Thread(target=ex_th, args=(i,))
    thread.start()

    print("Active Threads:", threading.active_count())
    print("Thread Obj:", threading.enumerate())