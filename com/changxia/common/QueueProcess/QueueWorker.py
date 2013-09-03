#!/usr/bin/python
#-*-coding:utf-8-*-

#############################################################
# Author    : Panfeng Lv <lvpanfeng@myhexin.com>
# Description: Multi Process Worker on Queue
# Revision  : $Id$
#############################################################

import sys,os
import time
from multiprocessing import Process,Queue,Pool
from Processor import Processor
from QueueProcess import QueueProcess

class QueueWorker:

    def __init__(self, queue, processor, queueServer, processCnt=4):
        """
            Parameters:
            - queue     :  multiprocessing Queue
            - processor :  参见 Processor类
            - queueServer : server obj
        """
        self.queue = queue
        self.processCnt = processCnt
        self.processor = processor
        self.queueServer = queueServer 
        self.plist = []
         
    def __del__(self):
        pass

    def queueWorker(self,queue):
        self.queueProcess = QueueProcess(queue,self.processor)
        self.queueProcess.run()
    
    def run(self):
        for i in xrange(self.processCnt):
            p = Process(target=self.queueWorker, args=(self.queue,))
            self.plist.append(p)
            p.start()
        if self.queueServer != None:
            self.queueServer.run()
            
        while True: time.sleep(10)

if __name__=="__main__":
    pass
