#/usr/bin/python
#-*-coding:utf-8-*-
from basiclogger import *
class test:
    
    def __init__(self, value):
        logging.info("init ..." + value)


    def process(self):
        logging.info("process ...")

  

if __name__ == "__main__":
    LOGGING("X")
    t = test("1")
    LOGGING("hello")
    test("2")
    LOGGING("X")
    test("3")

