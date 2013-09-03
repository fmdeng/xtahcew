#!/usr/bin/python
#-*-coding:utf-8-*-

#############################################################
# Author    : Panfeng Lv <lvpanfeng@myhexin.com>
# Description: Base App Web  
# Revision  : $Id$
#############################################################

import web
import os,sys
import logging
from multiprocessing import Queue
from Processor import Processor
from BaseQueueAppWeb import BaseQueueAppWeb

class AppTest(BaseQueueAppWeb):

    def __init__(self):
        BaseQueueAppWeb.__init__(self)

if __name__ == '__main__':
    urls = ('/test', 'AppTest',)
    #app = web.application(urls, globals(), autoreload=False)
    #web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    #app.run()
    queue = Queue()
    processor = Processor() 
    at = AppTest()
    app = web.application(urls, globals(), autoreload=False)
    at.init(app,queue,processor)
    at.run()
