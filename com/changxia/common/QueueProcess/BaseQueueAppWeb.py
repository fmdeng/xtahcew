#!/usr/bin/python
#-*-coding:utf-8-*-

#############################################################
# Author    : Panfeng Lv <lvpanfeng@myhexin.com>
# Description: Base App Web  
# Revision  : $Id$
#############################################################

import web
import traceback
import os,sys
import logging
import urllib
from setting_appweb import *
from multiprocessing import Queue

class BaseQueueAppWeb(object):

    SUBMIT_ACTION="SUBMIT"
    GET_ACTION="GET"
   
    AppObj = None
    QueueObj = None
    ProcessorObj = None
    def __init__(self):
        pass

    def Submit(self,parms):
        try:
            parms_decode = BaseQueueAppWeb.ProcessorObj.decodeJson(parms)
            if BaseQueueAppWeb.ProcessorObj.checkLastModify(parms) == False:
                logging.error("BaseQueueAppWeb Sumit Failed : checkLastModify")
                return "{\"status\":%d}" % STATUS_RTN["SUBMIT_ERROR_CHECK"] 
            BaseQueueAppWeb.QueueObj.put(parms_decode)
        except Exception,e:
            logging.error("BaseQueueAppWeb Submit Error : " + str(e))
            return "{\"status\":%d}" % STATUS_RTN["SUBMIT_ERROR_EXCEPTION"] 
        return "{\"status\":%d}" % STATUS_RTN["OK"] 
        
    def Get(self,parms):
        parms_decode = BaseQueueAppWeb.ProcessorObj.decodeJson(parms)
        return BaseQueueAppWeb.ProcessorObj.getValue(parms_decode)

    def serv(self):
        i = web.input()
        #handle = getattr(i,"handle",None)
        action = getattr(i,"action",None)
        parms = getattr(i,"parms",None)
        if action == BaseQueueAppWeb.SUBMIT_ACTION:
            res = self.Submit(parms)
        elif action == BaseQueueAppWeb.GET_ACTION:
            res = self.Get(parms)
        else:
            res = "{\"status\":%d}" % STATUS_RTN["UNKNOWN_ACTION"]
            logging.error("BaseQueueAppWeb serv Error : " + res)
        return res 

    def GET(self):
        return self.serv() 
    
    def POST(self):
        return self.serv()

    '''
    def run(self,urls,fvals,queue,processor):
        BaseQueueAppWeb.QueueObj = queue 
        BaseQueueAppWeb.ProcessorObj = processor 
        self.app = web.application(urls, fvals, autoreload=False)
        self.app.run() 
    '''

    def init(self,app,queue,processor):
        BaseQueueAppWeb.QueueObj = queue 
        BaseQueueAppWeb.ProcessorObj = processor 
        BaseQueueAppWeb.AppObj = app

    def run(self):
        BaseQueueAppWeb.AppObj.run() 

if __name__ == '__main__':
    pass
