#/usr/bin/python
#-*-coding:utf-8-*-

# the name of log dir   eg : ./log/2012-10-19.9949.process.log
LOG_DIR = "./log"

# the name of log file     eg:  ./log/2012-10-19.9949.process.log
LOG_NAME = "process"

# model type 
# if LOG_MODEL = 0  , always use only one log , no date time no pid  
#                    eg :  ./log/process.log
# if LOG_MODEL = 1  , the log name has data time and pid , one process make one log file    
#                    eg  :  ./log/2012-10-19.9949.process.log
LOG_MODEL = 0

# log format   eg : 10/19/2012 04:30:02 PM [INFO] Begin to run
LOG_FORMAT = "%(asctime)s [%(levelname)s] [filename:%(filename)s] [line:%(lineno)d] %(message)s"
DATA_LOG_FORMAT = "%m/%d/%Y %I:%M:%S %p"


# log level  debug | info | warning | error | critical ...
LOG_LEVEL = "info"




