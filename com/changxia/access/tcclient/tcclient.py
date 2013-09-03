#/usr/bin/python
#-*- coding:utf-8 -*-

import os
import sys
import re
import logging
import simplejson
from Classifiers.ClassifierServer import *
from Classifiers.ttypes import *

from thrift.Thrift import *

from thrift.transport import TSocket
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None

class TCClient():

    def __init__(self, host, port, classifier="", classids="/home/tcserver/TCServer/tconline/www/classifier/Industry_Concept_classid"):
        self.host = host
        self.port = port
        self.classifier = classifier
        self.client = None
        self.classids = classids
        return 
    
    def __del__(self):
        self.transport.close()
        return

    def close(self):
        try:
            self.transport.close()
        except TTransport.TTransportException, e:
            logging.warn("tcclient TTransportException %s"%(str(e) ) )
            #raise e
            return False
        except Exception, e:
            logging.warn("tcclient with connection failed: %s"%(str(e ) ) )
            return False
        return True

    def connect(self):
        ''' 
        Exceptions:
        raise ConnectionError exception when connection error
        '''
        try:
            socket = TSocket.TSocket(self.host,self.port) 
            self.transport = TTransport.TBufferedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
            self.client = Client(protocol)
            self.transport.open()
        except TTransport.TTransportException, e:
            logging.warn("tcclient connect failed:%s"%(str(e)))
            #raise e
            return False
        except Exception ,e:
            logging.warn("tcclient connect failed:%s"%(str(e)))
            return False
        return True

    def reconnect(self):
        try:
            f1 = self.close()
            f2 = self.connect()
            if f1 and f2:
                return True
        except Exception ,e:
            logging.warn("tcclient reconnect failed:%s"%(str(e)))
            #raise e
        return False

    def setClassifier(self, classifier):
        self.classifier = classifier
        return True

    def process(self, rawTitle, rawContent, title="", content="", pubtime="",  host= "", contentGroup="", additionalInformation="", uid = "test_uid", classifier = "yanbao"):
        docs = []
        doc = DocParam(uid, rawTitle, rawContent, title, content, pubtime, host, contentGroup, additionalInformation)
        docs.append(doc)
        try:
            resultList = self.client.TextPredict(docs)
            if resultList != None and len(resultList)==1:
                return resultList[0]
        except TTransport.TTransportException, e:
            logging.warn("tcclient connect failed:%s"%(str(e)))
            raise ConnectionError()
        except Exception ,e:
            logging.warn("tcclient connect failed:%s"%(str(e)))
        return None

    def classifyResults(self, processResult):
        if processResult == None:
            return {}
        pat = re.compile(".*<classify>([^<]+)</classify>.*")
        m = pat.match(processResult)
        results = {}
        if m != None:
            text = m.group(1).strip()
            tcs = text.split(" ")
            for tc in tcs:
                parts = tc.split(":")
                if len(parts) != 2:
                    continue
                results[parts[0]] = parts[1]
        return results

    def classifyJsonResults(self,processResult):
        result_dict = {}
        results = {}
        if processResult == "":
            return result_dict
        try:
            results = simplejson.loads(processResult)
        except Exception,e:
            logging.info("json loads wrong! content :%s" %processResult)
        classifyResults = results.get("classify",[])
        for rdict in classifyResults:
            for (tag,score) in rdict.items():
                result_dict[tag] = str(score)
        return result_dict
    def loadIdName(self, filename="/home/tcserver/TCServer/tconline/www/classifier/Industry_Concept_classid"):
        dict = {}
        lines = open(self.classids,"r").readlines()
        for item in lines:
            item = item.strip().split()
            dict[item[0]] = item[1]
        return dict
        pass
    def posNegContent(self, typename, attr_info):
        import types
        event_list = []
        cnt = 0
        dict = self.loadIdName()
        if 'instance' in attr_info :
            while cnt < len(attr_info['instance']):
                try:
                    instance = attr_info['instance'][cnt].encode("utf-8")
                    instanceID = attr_info['instanceID'][cnt].encode("utf-8")
                    relation = attr_info['relation'][cnt].encode("utf-8")
                    keywords = attr_info['keywords'][cnt].encode("utf-8")
                    instanceInTitle = attr_info['instanceInTitle'][cnt].encode("utf-8")
                    eventPos = attr_info['eventPos'][cnt].encode("utf-8")
                    eventCnt = attr_info['eventCnt'][cnt].encode("utf-8")
                    score = attr_info['score'][cnt].encode("utf-8")
                    instanceInFirPas = attr_info['eventInFirPas'][cnt].encode("utf-8")
                    event_list.append([ typename, str(score), "(%s, %s, %s, %s, %s, %s, %s, %s)"%(instance,instanceID, relation, keywords,instanceInTitle,eventPos,eventCnt,instanceInFirPas)])
                except:
                    event_list.append([typename, str(score), "(null, null, null,null, null,null,null,null)"])
                cnt+=1
        elif 'keywords' in attr_info:
            cnt = 0
            while cnt < len(attr_info['keywords']):
                score = attr_info['score'][cnt].encode("utf-8")
                keywords = attr_info['keywords'][cnt].encode("utf-8")
                instanceInTitle = attr_info['instanceInTitle'][cnt].encode("utf-8")
                eventPos = attr_info['eventPos'][cnt].encode("utf-8")
                eventCnt = attr_info['eventCnt'][cnt].encode("utf-8")
                instanceInFirPas = attr_info['eventInFirPas'][cnt].encode("utf-8")
                if typename.split("_")[0] in dict:
                    typename = dict[typename.split("_")[0]]
                event_list.append([typename, str(score), "(null, null, null,%s,%s,%s,%s,%s)"%(keywords,instanceInTitle,eventPos,eventCnt,instanceInFirPas)])
                cnt += 1
        return (True, event_list)

    def recognizeJsonResults(self,processResult, need_posneg=False):
        result_dict = {}
        neg_pos_data = []
        results = {}
        if processResult == "":
            return result_dict
        try:
            results = simplejson.loads(processResult)
        except Exception,e:
            logging.info("json loads wong! content :%s" %processResult)
        recoglist = results.get("recognition",[])
        for a in recoglist:
            for tag,bdict in a.items():
                recoglist = bdict.get("recognitions")
                s1 = ""
                for cdict in recoglist:
                    word = cdict.keys()[0]
                    vdict = cdict.values()[0]
                    TitleFre = vdict.get("TitleFre",0)
                    ContentFre = vdict.get("ContentFre",0)
                    Score = vdict.get("Score",0)
                    NormValue = vdict.get("NormValue","0")
                    NormID = vdict.get("NormID","0")
                    appearPos = vdict.get("firstAppear","0")
                    attr_info = vdict.get("Attr", "0")
                    #attr_info = "xxx"
                    s = "%s:%d:%d:%f:%s:%s:%s; " % (word.encode("utf-8"),TitleFre,ContentFre,Score,NormID,NormValue.encode("utf-8"), appearPos)
                    s1 += s
                    #print attr_info
                    if cmp(tag, "43004") == 0:
                        (flag, data) = self.posNegContent( word.encode("utf-8"), attr_info)
                        if flag == True:
                            for data_item in data:
                                neg_pos_data.append(data_item)
                result_dict[tag] = s1
        if need_posneg == True:
            return (result_dict,neg_pos_data)
        else:
            return result_dict

    def recognizeResults(self, processResult):
        if processResult == None :
            return {}

        recognize = re.compile(".*<recognition>([^<]+)</recognition>.*")
        m = recognize.match(processResult)
        results = {}
        if m != None:
            tps = m.group(1).strip().split("\t")
            for tp in tps:
                twds = tp.strip().split(" ")
                if len(twds) < 2:
                    continue

                tid = twds[0]
                wds = " ".join(twds[1:len(twds)])
                results[tid] = wds
        return results

    def predictDoc(self, doc):
        if doc == None:
            return ""
        docs = []
        docs.append(doc)
        try:
            resultList = self.client.TextPredict(docs)
            if resultList != None and len(resultList)==1:
                return resultList[0]
        except TTransport.TTransportException, e:
            logging.info("tcclient predict faield:%s"%(str(e)))
            raise e
        except Exception ,e:
            logging.info("tcclient predict failed:%s"%(str(e)))
            raise e
        return None

    def predictList(self, docs):
        if docs == None:
            return None
        resultList = self.client.TextPredict(docs)
        return resultList
    '''
    @brief 检查一段文本是否有有用的识别内容
    无用的识别内容：
    42542   其他其他
    43000   句子边界
    42998   股票过滤
    43004   正负面结果
    43003   正负面关键词
    43009   正负面肯定词
    43008   正负面否定词
    43010   正负面歧义词
    43011   无歧义词
    10010   人物
    32169   最长字句
    所有概念的id
    @return  True 含有财经相关的词, 以及分为概念，False 没有财经相关的词
    TODO
    如果含有识别id FinancialKeyword 那么改文章就是财经相关的文章
    '''
    def checkRecType(self, title, content, typeids=\
            set(["1000","42542", "43000", "42998", "43004", "43001", "43003", "43009", \
             "32169","43008", "43010", "43011","10010"])):
        processResult = ""
        try:
            processResult = self.process(title, content,additionalInformation="classifyFlag=0")
            conceptResult = self.process(title, content,additionalInformation="classifiersName=concept")
        except:
            logging.warn("TCServer wrong")
            return None
        result_dict = {}
        neg_pos_data = []
        results = {}
        print processResult
        if processResult == None or conceptResult == None:
            return None
        if processResult == "" and conceptResult == "":
            return False
        concepts = self.classifyJsonResults(conceptResult)
        for c in concepts:
            try:
                c_int = int(c)
                if c_int >= 2001 and c_int <= 2557:
                    return True
            except:
                continue
        try:
            results = simplejson.loads(processResult)
        except Exception,e:
            logging.warn("json loads wong! content :%s" %processResult)
            return False
        recoglist = results.get("recognition",[])
        for a in recoglist:
            try:
                tagid = int(a.keys()[0])
                if (tagid >= 32001 and tagid <= 32541) or (tagid >= 42001 and tagid <= 42557) \
                    or (tagid >= 200000 and tagid <= 400000):
                    continue
                if (a.keys())[0] not in typeids:
                    #print a.keys()[0]
                    return True
            except:
                logging.warn("recognition format wrong")
        return False


if __name__=="__main__":
    #数据准备
    title = ""
    content = """ 股市终于开始涨了，泪奔！ 刚在同花顺上查看了我的帐户，不知道偶亏得钱啥时候能赚回来。
    """
    #client 连接， 线上的IP: 192.168.200.46 192.168.200.59 192.168.200.91 , 客户端自己做好负载
    #content = ""
    client = TCClient("192.168.200.46", 9090)
    client.connect()
    print client.checkRecType(title, content)

    ''' 分类用的API '''
    #processResult = client.process(title, content,additionalInformation="classifiersName=concept")
    #print processResult
    #results = client.classifyJsonResults(processResult)
    #print  results
    #results = client.recognizeJsonResults(processResult)
    #for (key, val) in results.iteritems():
    #    print key +"\t"+val
