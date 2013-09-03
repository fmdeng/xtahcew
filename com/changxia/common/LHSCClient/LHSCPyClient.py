#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from gen_py.LHSC import LHSCServer 
from gen_py.LHSC.ttypes import *

class LHSCClient:

    def __init__(self, host, port):
        ''' 
        Exceptions:
        raise ConnectionError exception when connection error
        '''
        self.host = host
        self.port = port
        try:
            transport = TSocket.TSocket(host,port) 
            self.transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
            self.client = LHSCServer.Client(protocol)
            self.transport.open()
        except TTransport.TTransportException:
            raise ConnectionError()

    def __del__(self):
        self.transport.close()

    def Segment(self, uid, content, clausePositionGap, sentencePositionGap, needSimhash):
        ret = self.client.Segment(uid, content, clausePositionGap, sentencePositionGap, needSimhash)
        return ret 

    def GenMixSegment(self,uid,title,content, clausePositionGap, sentencePositionGap, needTC=0):
        ret = self.client.GenMixSegment(uid,title,content, clausePositionGap,sentencePositionGap,needTC)
        return ret

class SeggerClient:
   
    def __init__(self, host, port, swfile=None):
        self.stopwords = set() 
        if swfile != None:
            self.swLoad(swfile)
        self.lhscclient = LHSCClient(host,port) 
    
    def swLoad(self,swfile):
        '''
           load stopword
        '''
        fhandle = open(swfile)
        fileList = fhandle.readlines()
        for fileline in fileList:
           self.stopwords.add(fileline.strip())
        fhandle.close()

    def tokenSplit(self,token):
        w = None
        wpos = None
        if token == "":
            return (w,wpos)
        rpos = token.rfind("/")
        if rpos != -1:
            w = token[0:rpos]
            wpos = token[rpos+1:]
        return (w,wpos)

    def parseContent(self,value):
        vstr = "" 
        rwl = []
        rws = []
        vlist = value.strip().split()
        vlen = len(vlist)
        i = 0
        while i < vlen:
            token = vlist[i].strip()
            (w,wpos) = self.tokenSplit(token)
            if w != None:
                if i + 1 < vlen:
                    token_a = vlist[i+1].strip()
                    (w_a,wpos_a) = self.tokenSplit(token_a)
                    if w_a != None:
                        if wpos_a == wpos:
                            if i + 2 < vlen:
                                token_b = vlist[i+2].strip()
                                (w_b,wpos_b) = self.tokenSplit(token_b)
                                rwl.append(w)
                                if w_b != None:
                                    if wpos_b == wpos_a:
                                        i = i + 4
                                        rws.append((w_a,1))
                                        vstr += w_a
                                    else:
                                        if w == w_a + w_b:
                                            i = i + 3 
                                            rws.append((w,0))
                                            vstr += w
                                        else:
                                            i = i + 2
                                            rws.append((w_a,1))
                                            vstr += w_a
                                else:
                                    i = i + 3
                                    rws.append((w_a,0))
                                    vstr += w_a
                                continue
                        else:
                            rwl.append(w)
                            rws.append((w,0))
                            vstr += w
                    else:
                        rwl.append(w)
                        rws.append((w,0))
                        vstr += w
                        i = i + 2
                        continue
                else:
                    rwl.append(w)
                    rws.append((w,0))
                    vstr += w
            i = i + 1

        return (vstr,rwl,rws)

    def getSegment(self, uid, content):
        rwords = []
        ret = self.lhscclient.Segment(uid, content, 2, 3, 0) 
        (rwl,rws,vstr) = self.parseContent(ret.content)
        
        for item in rws: 
            if item not in self.stopwords:
                rwords.append(item)

        return rwords

    def getGenMixSegment(self,uid,title,content,clausePositionGap=2,sentencePositionGap=3,needTC=0):
        return self.lhscclient.GenMixSegment(uid,title,content,clausePositionGap,sentencePositionGap,needTC) 

if __name__ == '__main__':
   client = SeggerClient("192.168.23.11",8000)
   s = "晨鸣纸业是个好公司，浦发银行是个好公司, 分词测试程序"
   r = client.getSegment("testuid",s) 
   #for item in r:
   #    print item 
   r = client.getGenMixSegment("testuid",s,"")
   print r.title
