#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
import logging
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from gen_py.Ltp import LtpServer 
from gen_py.Ltp.ttypes import *

class LtpClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.logger = logging.getLogger()
    
    def __del__(self):
        self.transport.close()

    def connect(self):
        ''' 
        Exceptions:
        raise ConnectionError exception when connection error
        '''
        try:
            transport = TSocket.TSocket(self.host,self.port) 
            self.transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
            self.client = LtpServer.Client(protocol)
            self.transport.open()
            return True
        except TTransport.TTransportException:
            raise ConnectionError()
            self.logger.error("(%s,%d) server connect error:TTransportException" % (self.host,self.port))
            return False
        except :
            self.logger.error("(%s,%d) server connect error:unknown" % (self.host,self.port))
            return False

    def Segment(self, content, needPos,isPhrase=0):
        ret = "" 
        flag = True 
        try:
            ret = self.client.Segment(content, needPos, isPhrase)
        except Thrift.TException, tx:
            print "%s" % (tx.message)
            self.logger.error("%s" % (tx.message))
            flag = False
        return (ret,flag)

    def MixSegment(self, content, clausePositionGap, sentPositionGap, needPos, isPhrase=1):
        ret = "" 
        flag = True 
        try:
            ret = self.client.MixSegment(content, clausePositionGap, sentPositionGap,needPos,isPhrase)
        except Thrift.TException, tx:
            print "%s" % (tx.message)
            self.logger.error("%s" % (tx.message))
            flag = False
        return (ret,flag)

    def MixSegmentParse(self,content, clausePositionGap, sentPositionGap, needPos, isPhrase=1, needParse=1):
        ret = "" 
        flag = True 
        try:
            ret = self.client.MixSegmentParse(content, clausePositionGap, sentPositionGap,needPos,isPhrase, needParse)
        except Thrift.TException, tx:
            print "%s" % (tx.message)
            self.logger.error("%s" % (tx.message))
            flag = False
        return (ret,flag)
        
    def KeyWords(self, content, isPhrase):
        ret = ""
        try:
            ret = self.client.KeyWords(content,isPhrase)
        except Thrift.TException, tx:
            print "%s" % (tx.message)
            return ""
        return ret

    def dictReload(self):
        ret = None
        flag = True 
        try:
            ret = self.client.DictReload()  
        except Thrift.TException, tx:
            self.logger.error("%s" % (tx.message))
            flag = False

        return (ret,flag)


class SeggerClient:
   
    def __init__(self, hosts,swfile=None):
        self.hosts = hosts
        self.ltpclient = None
        self.stopwords = set()
        if swfile != None:
            self.swLoad(swfile)

    def connect(self):   
        for (h,p) in self.hosts:
            client = LtpClient(h,p)
            if client.connect() == True:
                self.ltpclient = client
                return True
        return False 

    def swLoad(self,swfile):
        '''
           load stopword
        '''
        try:
            fhandle = open(swfile)
            fileList = fhandle.readlines()
            for fileline in fileList:
               self.stopwords.add(fileline.strip())
            fhandle.close() 
        except IOError:
            logging.error("%s IOError" % swfile)

    def tokenSplit(self,token,flag,order=1):
        w = "" 
        _w = ""
        if token == "" or token == None:
            return (w,_w)
        if order == 0:
            rpos = token.find(flag)
        else:
            rpos = token.rfind(flag)
        flen = len(flag)
        if rpos != -1:
            w = token[0:rpos]
            _w = token[rpos+flen:]
        return (w,_w)

    def splitResult(self,r,denoising):
        ra = ""
        rb = ""
        rlist = r.strip().split(" ")
        for item in rlist:
            item = item.strip()
            (w,_w) = self.tokenSplit(item,"/")
            if w in self.stopwords:
                continue
            (_wl,_wr) = self.tokenSplit(_w,":",0)
            if denoising == 1:
                (_wtype,_wtyper) = self.tokenSplit(_wr,":",0)
                if _wtype == "0" or _wtype == "1":
                    continue
            ra = ra + "%s/%s " % (w,_wl)
            rb = rb + "%s/%s:%s " % (w,_wl,_wr)
        ra = ra.strip()
        rb = rb.strip() 
        return (ra,rb)

    def filter(self,srcstr,flag):
        ret = ""
        rlist = srcstr.strip().split(" ")
        if flag == 0:
            for item in rlist:
                item = item.strip()
                if item in self.stopwords:
                    continue
                ret = ret + "%s " % item
        else: 
            for item in rlist:
                item = item.strip()
                (w,_w) = self.tokenSplit(item,"/")
                if w == "" or w in self.stopwords:
                    continue
                ret = ret + "%s/%s " % (w,_w)
        ret = ret.strip()
        return ret

    def tokenPosSplit(self,token):
        (words,wordsInfo) = self.tokenSplit(token,"/",1)
        if wordsInfo == "":
            return (words,None,wordsInfo)
        if wordsInfo.find(":") != -1:
            (wordsPos,wordsOtherInfo) = self.tokenSplit(wordsInfo,":",0)
            try:
                wordsPos = int(wordsPos)
                wordsPos = str(wordsPos)
            except Exception, e:
                wordsPos = None
        else:
            try:
                wordsPos = int(wordsInfo)
                wordsPos = str(wordsPos)
            except Exception, e:
                wordsPos = None
        return(words,wordsPos,wordsInfo)

    def extractMixSegment(self,content):
        bigParticle = []
        smallParticle = []
        if content == "":
            return ("","")
        wlist = content.strip().split(" ")
        wlen = len(wlist)
        idx = 0
        addStop = 4
        while idx < wlen:
            token = wlist[idx].strip()
            (words,wordsPos,wordsInfo) = self.tokenPosSplit(token)
            if words != None and wordsPos != None:
                if idx + 1 < wlen:
                    token_a = wlist[idx+1].strip()
                    (words_a,wordsPos_a,wordsInfo_a) = self.tokenPosSplit(token_a)
                    if words_a != None and wordsPos_a != None:
                        if wordsPos_a == wordsPos:
                            idx_ = idx + 2
                            addWords = words_a
                            bigParticle.append(token)
                            smallParticle.append(token_a)
                            while idx_ < wlen and idx_ - idx <= addStop:
                                token_idx_ = wlist[idx_].strip()
                                (words_idx_,wordPos_idx_,wordsInfo_idx_) = self.tokenPosSplit(token_idx_)
                                addWords += words_idx_
                                smallParticle.append(token_idx_)
                                if words == addWords:
                                    break
                                idx_ += 1
                            idx = idx_ + 1
                            continue
                        else:
                            pass
                            bigParticle.append(token)
                            smallParticle.append(token)
                    else:
                        pass
                        idx = idx + 2
                        bigParticle.append(token)
                        smallParticle.append(token)
                        continue
                else:
                    pass
                    bigParticle.append(token)
                    smallParticle.append(token)
            idx = idx + 1
        return (" ".join(bigParticle)," ".join(smallParticle))
        
    def getSegment(self, content, needPos=1, isPhrase=0):
        (ret,flag) = self.ltpclient.Segment(content,needPos,isPhrase) 
        r = self.filter(ret,needPos)
        return (r,flag)

    def getMixSegment(self, content, needPos=1,isPhrase=1,denoising=1):
        (ret,flag) = self.ltpclient.MixSegment(content, 5, 10, needPos,isPhrase)
        if flag == True:
            (a,b) = self.splitResult(ret,denoising)
            return (a,b,flag)
        else: 
            return ("","",flag)     

    def getMixSegmentParse(self, content, needPos=1, isPhrase=1, denoising=0):
        (ret,flag) = self.ltpclient.MixSegmentParse(content, 5, 10, needPos,isPhrase)
        if flag == True:
            (a,b) = self.splitResult(ret,denoising)
            return (a,b,flag)
        else: 
            return ("","",flag)     
    
    def getKeyWords(self,content,isPhrase=0):
        ret = self.ltpclient.KeyWords(content,isPhrase)
        return ret

if __name__ == '__main__':
    client = SeggerClient([("192.168.23.32",8001)])
    print client.connect()
    s = "郭树清"
    s = "吴海胖"
    s = "吕攀峰"
    s = "陶志伟"
    #s = "中国农业银行"
    #s = "7月经济数据下周密集发布CPI或降至1时代"
    #s = "中国银行 两房"
    #s = "麦迪电器的上市定位"
    #s = "上市公司20强排名"
    #s = "与朝鲜有关的股票"
    #s = "炒股“实用”T+0方法"
    #s = "净利润 下降"
    #s = "cpi facebook abcedf gdp"
    #(r,flag) = client.getSegment(s,1,1)
    #print r
    #print flag
    #print
    s="雅戈尔割肉４．８亿元退地%20成本或是退地主因"
    (a,b,flag) = client.getMixSegment(s,1,1,0) 
    #print a
    print b
    #(a,b,flag) = client.getMixSegmentParse(s) 
    #print a
    #print b
    #(c,d) = client.extractMixSegment(b)
    #print 
    #print c
    #print d
    #print client.getKeyWords(s)
