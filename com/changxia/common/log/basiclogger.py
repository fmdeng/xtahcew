#/usr/bin/python
#-*-coding:utf-8-*-
import logging
import logging.handlers
import os
import sys
try:
    from log_config import *
except:
    LOG_DIR = "./log"
    LOG_NAME = "process"
    LOG_MODEL = 0
    LOG_FORMAT = "%(asctime)s [%(levelname)s] [filename:%(filename)s] [line:%(lineno)d] %(message)s"
    DATA_LOG_FORMAT = "%m/%d/%Y %I:%M:%S %p"
    LOG_LEVEL = "info"
import time

class LOGGING:

    def __init__(self, log_name=LOG_NAME):
        self.initConfig(log_name)

    def initConfig(self, log_name):
        try:
            if not os.path.exists(LOG_DIR):
                os.system("mkdir -p %s" % LOG_DIR)
        except:
            sys.stderr.write("can not create log dir " + LOG_DIR + ", the log does not work! please check your access right\n \
            you can mkdir the dir by hand\n")
            return
        log_file = log_name
        if log_file.find("/") <> 0:
            if LOG_MODEL == 0:
                current_data = self.getData() 
                log_file =  LOG_DIR + "/" + "%s.log"%(log_name)
            else:
                current_data = self.getData() 
                pid = os.getpid()
                log_file = LOG_DIR + "/" + current_data +"." + str(pid)+ ".%s.log"%(log_name)
        formatter = logging.Formatter( fmt=LOG_FORMAT, datefmt=DATA_LOG_FORMAT)
        my_logger = logging.getLogger()
        self.setLevel(my_logger)
        try:
            handler = logging.handlers.TimedRotatingFileHandler(log_file, 'midnight',1)
        except:
            sys.stderr.write("can not create log file " + log_file + " , the log does not work! please check your access right\n \
            you can mkdir the dir by hand\n")
            return

        handler.setFormatter(formatter)
        my_logger.addHandler(handler)


    def setLevel(self, log_object):
        if LOG_LEVEL == "warning":
            log_object.setLevel(logging.WARNING)
        elif LOG_LEVEL == "debug":
            log_object.setLevel(logging.DEBUG)
        elif LOG_LEVEL == "error":
            log_object.setLevel(logging.ERROR)
        elif LOG_LEVEL == "critical":
            log_object.setLevel(logging.CRITICAL)
        else:
            log_object.setLevel(logging.INFO)

    def getData(self, format="%Y-%m-%d"):
        times = time.time()
        date_time_str = time.strftime(format, time.localtime(times))
        return date_time_str


