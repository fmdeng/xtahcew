#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
import os
sys.path.append("../../../")
from common.TimeHelper import *
from common.log.logger import *
from setting import *
import urllib
import urllib2
import json
import time
import types
import random
import traceback
"""
以urllib.open的方式访问solr的结果

"""

class SolrReaderUtil:

    def __init__(self, solr_url, reconnect_maxcnt=2):
        """ eg : http://192.168.201.63:10000/solr/select? """ 
        self.solr_url = solr_url
        self.timeHelper = TimeHelper()
        self.reconnect_cnt = 0
        self.reconnect_maxcnt = reconnect_maxcnt
        self.addressType = self.addressIsList()
    
    def addressIsList(self):
        if type(self.solr_url) == types.ListType:
            return True
        else:
            return False

    def constructSolrQuery(self, query, param_else={}, fq=[]):
        param_dict = {}
        param_dict["wt"] = "json"
        param_dict["distrib"] = "true"
        param_dict["q"] = query
        for param,value in param_else.items():
            param_dict[param] = value
        try:
            param_str = urllib.urlencode(param_dict) 
            if len(fq) <> 0:
                plus_str = "&".join(["fq=%s" %afq for afq in fq])                
                param_str += "&" + plus_str
        except:
            logging.warn("urlencode dict failed!")
            return ""
        if self.addressType:
            solr_url = [ (address + param_str) for address in self.solr_url]
        else:
            solr_url = self.solr_url + param_str
        return solr_url

    def connect(self, solr_url):
        """ connect solr """
        line = ""
        try:
            req = urllib2.Request(solr_url)
            #print solr_url
            if solr_url.find("201.") <> -1:
                req.set_proxy(PROXY_ADDRESS, "http")
            line = urllib2.urlopen(req).read()
            #print line
        except:
            #print(traceback.format_exc())
            logging.warn("solr connect failed ! solr down ? address : %s  !reconnect %d times" %(solr_url,self.reconnect_cnt))
            return line
        return line

    def reconnect(self, solr_url):
        """ reconnect """
        self.reconnect_cnt += 1
        return self.connect(solr_url)

    def accessSolr(self, solr_url):
        """ connect or else reconnect """
        line = ""
        if self.addressType:
            addresslist = solr_url[:]
            cnt = 0
            while( len(addresslist) > 0 and cnt <= self.reconnect_maxcnt):
                num = random.randint(0,len(addresslist)-1)
                logging.info("connect address : %s" %addresslist[num])
                line = self.connect(addresslist[num])
                if line <> "":
                    break
                cnt += 1
                del addresslist[num]
        else:
            line = self.connect(solr_url)
            if line == "":
                for x in xrange(self.reconnect_maxcnt):
                    line = self.reconnect(solr_url)
                    if line != "":
                        break
                    #time.sleep(2)
        return line

    @staticmethod
    def parserClassification(classiferStr):
        """
        # classiferStr : Classification 字段内容 eg : -1:0.979535 1000000:1 1075:0.725315 
        # return : dict key : cid ; value : score(string)
        """
        cid2score = {}
        if classiferStr == None:
            logging.info("the Classification is null")
            return cid2score
        cid2scorelist = classiferStr.strip().split()
        for cidinfo in cid2scorelist:
            clist = cidinfo.strip().split(":")
            if len(clist) <> 2:
                continue
            cid2score[clist[0]] = clist[1]
        return cid2score

    @staticmethod
    def parserRelatedStock(stockstr):
        """
        # stockstr : RelatedStock 字段内容
        # return  : dict  key : stock code ;value : (score , titleFre, contentFre)
        """
        stock2info = {}
        if stockstr == None:
            logging.info("the RelatedStock is null")
            return stock2info
        stocklist = stockstr.strip().split()
        length = len(stocklist)
        if length % 2 <> 0:
            logging.warn("the RelatedStock format is wrong!")
            return stock2info
        for x in xrange(length):
            if x % 2 == 1:
                continue
            try:
                score = (stocklist[x+1].split(":")[0])
                titFre = (stocklist[x+1].split(":")[1])
                conFre = (stocklist[x+1].split(":")[2])
                stock2info[stocklist[x].strip()] = (score, titFre, conFre)
            except:
                #print(traceback.format_exc())
                logging.warn("the RelatedStock format is wrong! float chang wrong")
                continue
        return stock2info

    @staticmethod
    def parserRelatedSecurity(stockstr):
        """
        # stockstr : RelatedSecurity 字段内容
        # return  : dict  key : stock code ;value : [score , titleFre, contentFre, stockType]
        """
        stock2info = {}
        if stockstr == None:
            logging.info("the RelatedStock is null")
            return stock2info
        stocklist = stockstr.strip().split()
        length = len(stocklist)
        if length % 2 <> 0:
            logging.warn("the RelatedStock format is wrong!")
            return stock2info
        for x in xrange(length):
            if x % 2 == 1:
                continue
            try:
                infolist = stocklist[x+1].split(":")
                stock2info[stocklist[x].strip()] = infolist
            except:
                #print(traceback.format_exc())
                logging.warn("the RelatedSecurity format is wrong!")
                continue
        return stock2info

    def loadJsonSolr(self, solr_res):
        """
        # solr_res : solr result json_str
        # return : solr result json_format
        """
        json_format = {}
        try:
            json_format = json.loads(solr_res)
        except:
            logging.warn("load json result of solr failed!")
            return False,json_format
        return True,json_format

    def getSolrInfo(self, solr_res, param_set=set()):
        """
        # solr_res :  solr result json
        # param_set : 需要获取结果的字段名,空则全部结果
        # return :  list  = [dict1,dict2 ...] ,每个dict为 字段名 对应 结果
        """
        paramlist = []
        flag,json_format = self.loadJsonSolr(solr_res)
        if "response" in json_format:
            if "docs" in json_format["response"]:
                reslist = json_format["response"]["docs"]
            else:
               logging.warn("json format wrong! has no docs tag!")
               return False,paramlist
        else:
            logging.warn("json format wrong! has no response tag!")
            return False,paramlist
        #reslist.sort(key=lambda s:s["PublishTime"],reverse = True)
        #print reslist
        if len(param_set) == 0:
            return True,reslist
        for res in reslist:
            paramdict = {}
            try:
                for param in param_set:
                    content = res.get(param)
                    paramdict[param] = content
            except:
                continue
            paramlist.append(paramdict)
        #print paramlist
        return True,paramlist

    def addTimeToQuery(self, last_day=5, end_day=""):
        """
        # last_day : days 
        # end_day format :  %Y-%m-%d  eg : 2012-12-04
        # if end_day == "" : 
        #   end_day = time.time()
        """
        if end_day == "":
            end_seconds = int(time.time())
        else:
            end_data = end_day + " 00:00:00"
            end_seconds = self.timeHelper.getSecondsFromDateTime(end_data)
        begin_seconds = end_seconds - last_day * 3600 * 24
        fq = "PublishTime:[" + str(begin_seconds) + " TO " +str(end_seconds) +  "]" 
        return fq

class SolrReader:
    
    def __init__(self, solr_url,reconnect_maxcnt = 2):
        self.solrReaderUtil = SolrReaderUtil(solr_url, reconnect_maxcnt)

    def process(self, query, need_param=set(), rows=0, last_day=5, end_day="",  fq=[], solr_param={}):
        """
        # @param query :  solr query
        # @param solr_param : dict, solr其他需要加的参数 ,
        # @param need_param : set, 需要的solr字段
        # @param rows : solr 搜索参数
        # @param fq : list 支持多个fq参数，eg : fq=["Classification:2000","Classification"]
        # @param lasy_day : solr搜索时间天数, 结束时间以 end_day 为准
        # @param end_day : solr搜索的结束时间, format :  %Y-%m-%d  eg : 2012-12-04
        # return : flag , true or false
        #          list , list里的每个元素是一个dict, dict的key是need_param中的字段
        """
        if "fq" not in solr_param:
            fq_time = self.solrReaderUtil.addTimeToQuery(last_day, end_day)
            solr_param["fq"] = fq_time
        if rows <> 0:
            solr_param["rows"] = rows
        solr_address = self.solrReaderUtil.constructSolrQuery(query, solr_param ,fq)
        if solr_address == "" or len(solr_address) == 0:
            return False,[]
        line = self.solrReaderUtil.accessSolr(solr_address)
        if line == "":
            return False,[]
        flag,reslist = self.solrReaderUtil.getSolrInfo(line, need_param)
        if not flag:
            return False,[]
        else:
            return True,reslist
            
    def getSolrRawResult(self, query, rows=0, last_day=5, end_day="", fq=[], solr_param={}):
        """
        # all param as the same as process
        # return flag : true or false
        #        json_format : the solr raw result (has json_load)
        """
        if "fq" not in solr_param:
            fq_time = self.solrReaderUtil.addTimeToQuery(last_day, end_day)
            solr_param["fq"] = fq_time
        if rows <> 0:
            solr_param["rows"] = rows
        solr_address = self.solrReaderUtil.constructSolrQuery(query, solr_param, fq)
        if solr_address == "" or len(solr_address) == 0:
            return False,[]
        line = self.solrReaderUtil.accessSolr(solr_address)
        if line == "":
            return False,[]
        return  self.solrReaderUtil.loadJsonSolr(line)
        

    @staticmethod
    def parserRelatedStock(stockstr):
        """
        # stockstr : RelatedStock 字段内容  eg : '444444 6.448696:1:14 300033 0.500000:0:1'
        # return  : dict  key : stock code ;value : (score , titleFre, contentFre)
        """
        return SolrReaderUtil.parserRelatedStock(stockstr)

    @staticmethod 
    def parserClassification(classiferStr):
        """
        # classiferStr : Classification 字段内容 eg : -1:0.979535 1000000:1 1075:0.725315 
        # return : dict key : cid ; value : score(string)
        """
        return SolrReaderUtil.parserClassification(classiferStr)

    @staticmethod
    def parserRelatedSecurity(stockstr):
        """
        # stockstr : RelatedSecurity 字段内容
        # return  : dict  key : stock code ;value : [score , titleFre, contentFre, stockType]
        """
        return SolrReaderUtil.parserRelatedSecurity(stockstr)

    def accessSolrByMonth(self, query, month, prows, raw_fq=[], raw_param={}):
        """
        #提供按月搜索新闻,使搜到的新闻尽可能的分散
        # @param query : 
        # @param month : 搜索的月数
        # @param prows : 每个月搜索量
        # 其余参数同上
        # return ： 同上 list
        """
        reslist = []
        nowtime = time.time()
        month_day = 30
        timeHelper = TimeHelper()
        for x in xrange(month):
            end_time = nowtime - x * month_day
            current_end_day = timeHelper.getDateTimeFromSeconds(end_time, "%Y-%m-%d")
            flag,curreslist = self.process(query, rows=prows, last_day=month_day, end_day=current_end_day, fq=raw_fq, solr_param=raw_param)
            if flag:
                reslist.extend(curreslist)
        return reslist


if __name__ == "__main__":
    solr_url = "http://192.168.201.68:10100/solr/select?"
    #solr_url = ["http://192.168.201.63:10000/solr/select?","http://192.168.201.61:10000/solr/select?"]
    solrreader = SolrReader(solr_url)
    (flag,reslist) = solrreader.process("300033",need_param=set(["UID","PageRawTitle","RelatedStock"]), fq=["Classification:90","-Classification:2000000"], rows=10)
    print flag
    print reslist[0]
    print "-----"
    (flag,json_format) =  solrreader.getSolrRawResult("300033")
    print flag
    print json_format
    print "-----"
    print SolrReader.parserRelatedStock(reslist[0].get(u"RelatedStock"))
    print "-----"
    classiferStr = u"1:0.995212 113:0.148317 114:0.851683 130:0.33084 131:0.66916"
    print SolrReader.parserClassification(classiferStr)
    print "-----"
    reslist = solrreader.accessSolrByMonth("300033", 5, 10)
    print reslist[0]
