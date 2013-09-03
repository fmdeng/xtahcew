#/usr/bin/python
#-*-coding:utf-8-*-

import os
import sys
sys.path.append(os.getcwd())
sys.path[0] = os.getcwd()
sys.path.append("../..")
from setting import *
from kazoo.client import KazooClient
import re
import logging
''' kazoo : http://kazoo.readthedocs.org/en/latest/basic_usage.html '''
class ReadSetting:

    def __init__(self, zookeeper_host=None):
        self.zk = self.initZK(zookeeper_host)
        self.zookeeper_host = zookeeper_host
    ''' disconnect '''
    def __del__(self):
        if self.zk != None:
            self.zk.stop()

    def reconnect(self):
        if self.zk != None:
            self.zk.stop()
        self.zk = self.initZK(self.zookeeper_host)

    '''  connect and start '''
    def initZK(self, zookeeper_host=None):
        zk = None
        try:
            if zookeeper_host == None:
                zk = KazooClient(hosts=ZOOKEEPER_HOST)
            else:
                zk = KazooClient(hosts=zookeeper_host)
            zk.start()
        except Exception,e:
            logging.warn("zookeeper connect problem : %s" %str(e))
        return zk

    ''' _ change to /  '''
    def changeFormat(self,rlist):
        for x in xrange(len(rlist)):
            temp = rlist[x]
            temp = re.sub("_","/",temp)
            rlist[x] = temp

    ''' get the childnode from given node '''
    def getSettingData(self, node):
        if self.zk == None:
            logging.warn("hasnot connect to zookeeper, reconnect!")
            self.reconnect()
            if self.zk == None:
                logging.warn("reconnect failure! need get config from setting!")
                return None
        if not self.zk.exists(node):
            logging.warn("the node dose not exist!")
            return None
        rlist = self.zk.get_children(node)
        if len(rlist) == 0:
            logging.warn("the node has no child node!")
            return None
        self.changeFormat(rlist)
        rlist = self.checkURL(rlist)
        return rlist

    def checkURL(self,rlist):
        templist = []
        for url in rlist:
            if url.find("http") == -1:
                url = "http://" + url
            if url[-1] == "/":
                url = url[:-1]
            templist.append(url)
        return templist

if __name__ == "__main__":
    rs = ReadSetting()
    res = rs.getSettingData("/LIVE_AGGREGATOR/cmqtype")
    print res
