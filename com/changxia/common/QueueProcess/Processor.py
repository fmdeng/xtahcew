#!/usr/bin/python
#-*-coding:utf-8-*-

#############################################################
# Author    : Panfeng Lv <lvpanfeng@myhexin.com>
# Description: Processor interface 
# Revision  : $Id$
#############################################################

import sys,os
import time
import multiprocessing

class Processor(object):

    def __init__(self):
        pass

    def __del__(self):
        pass

    def __call__(self,parms):
        return self.process(parms)

    def checkLastModify(self,parms):
        return True

    def setValue(self,parms):
        '''存放结果'''
        pass

    def getValue(self,parms):
        pass
        '''获取结果'''
        return "return GetValue" 

    def decodeJson(self,parms):
        '''参数转换,parms为json格式(unicode),输出process/getValue需要的结构'''
        return "" 

    def process(self,parms):
        print "Processor : ",os.getppid(),os.getpid(),parms,multiprocessing.current_process().name
        return ""

if __name__=="__main__":
    pass
