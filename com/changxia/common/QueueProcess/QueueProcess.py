#!/usr/bin/python
#-*-coding:utf-8-*-

#############################################################
# Author    : Panfeng Lv <lvpanfeng@myhexin.com>
# Description: Process on Queue
# Revision  : $Id$
#############################################################

import sys,os
import time
import logging
import multiprocessing
from multiprocessing import Process,Pool

class QueueProcess:

    def __init__(self, queue, processor):
        self.queue = queue
        self.processor = processor
        #self.pool = Pool(processCnt,None,queue)

    def __del__(self):
        pass

    def run(self):
        while True:
            while self.queue.empty() != True: 
                in_parms = self.queue.get()
                logging.info("Processing [%s]" % (multiprocessing.current_process().name))
                topics = self.processor.process(in_parms)
            logging.info("QueueProcess Queue Emtpy : %s" % multiprocessing.current_process().name)
            time.sleep(10)

if __name__=="__main__":
    pass
