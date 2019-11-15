#-*- coding:utf-8 -*-
import threading
list=[]
def test1():
    for i in range(1,100):
        list.append(i)

t1=threading.Thread(target=test1)
t1.start()

import time

time.sleep(3)

def test2():
    print(list.pop())

t2=threading.Thread(target=test2)
t2.start()