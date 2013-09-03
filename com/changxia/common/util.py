#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
import logging
import time
import os
import re
sys.path.append("..")
import logging.handlers
import types
from setting import *
'''
定义了系统相关的函数：
报警、拷贝文件，move文件，判断文件是否一样
'''

def runCommand(cmd_str, msg,  result_ok = True, report=True):
    '''
    执行系统命令:
    @param cmd_str 系统命令
    @param msg 失败的时候返回的信息
    @param result_ok  True， 如果系统返回0，那么该函数返回True，否则退出或者返回False
                      False，如果系统返回非0，那么该函数返回False，否则退出或者返回False
    @param report  True， 报警&退出， False，返回False
    '''

    logging.info(cmd_str)
    status = os.system(cmd_str)
    if status <> 0 and result_ok == True and report == True:
        reportNagios(msg, NAGIOS_CRITICAL)
        sys.exit(1)
    if status == 0 and result_ok == False and report == True:
        reportNagios(msg, NAGIOS_CRITICAL)
        sys.exit(1)
    if (status == 0 and result_ok == False ) or ( status <> 0 and result_ok==True) :
        return False
    return True

def reportNagios(msg='memory ok', level="0", type_name="HotKeyWords", nagios_host=NAGIOS_HOST):
    '''
    报警
    '''
    hostname = os.popen("hostname -I").read()
    hostname = hostname.strip()
    if os.path.exists(NAGIOS_BIN) == True:
        logging.info( "echo \"%s\t%s\t%s\t%s\" | %s %s"%(hostname, type_name, level, msg , NAGIOS_BIN, nagios_host) )
        os.system("echo \"%s\t%s\t%s\t%s\" | %s %s"%(hostname, type_name, level, msg , NAGIOS_BIN, nagios_host))
    else:
        pass

'''获得当前时间到秒'''
def currentTime():
    time_str = os.popen("""date "+%Y-%m-%d-%H-%M-%S" """).read()
    time_str = time_str.strip()
    return time_str

def backFile(filename, back_file_dict={}):
    '''备份文件'''
    time_str = currentTime()
    cmd_str = "mv %s %s.%s"%(filename, filename, time_str)
    back_file_dict["%s.%s"%(filename, time_str)] = 1
    return runCommand(cmd_str, "back %s"%(filename) )

def mv(filename, filename_two):
    '''移动文件'''
    cmd_str = "mv %s %s"%(filename, filename_two)
    return runCommand(cmd_str, "mv %s %s"%(filename, filename_two) )

def cp(filename, filename_two):
    '''拷贝文件'''
    cmd_str = "cp %s %s"%(filename, filename_two)
    return runCommand(cmd_str, "mv %s %s"%(filename, filename_two) )

def fileEqual(filename_one, filename_two):
    '''判断两个文件是否相同'''
    cmd_str = "ls  " + filename_one + " >/dev/null 2>&1"
    if runCommand(cmd_str, "check file %s "%(filename_one), False, False ):
        return False
    cmd_str = "ls " + filename_two + " >/dev/null 2>&1"
    if runCommand(cmd_str, "check file  %s "%(filename_two), False, False ):
        return False
    md5_one = os.popen("md5sum "  + filename_one).read().strip().split()[0]
    md5_two = os.popen("md5sum "  + filename_two).read().strip().split()[0]
    if cmp(md5_two, md5_one) == 0:
        logging.info("%s %s is same"%(filename_one, filename_two) )
        return True
    else:
        logging.info("%s %s is not same"%(filename_one, filename_two) )

        return False

if __name__ == "__main__":
    pass
