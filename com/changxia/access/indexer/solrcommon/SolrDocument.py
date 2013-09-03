#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
sys.path.append("../../../")
from access.indexer.solrcommon.solr.core import *
from access.indexer.solrcommon.solr.paginator import *
from common.util import *
from common.EncodeUtil import *
from setting import *
import logging
import json
import time
import traceback

class SolrDocument:
    
    RESPONSE_TAG="response"
    HEADER_TAG = "responseHeader"
    QTIME_TAG = "QTime"
    
    """connect solr"""
    def __init__(self, solr_address):
        self.solr_address = solr_address
        self.doc_added_num = 0
        self.error_cnt = 0
        self.solrConnection = None
        self.connect()
        logging.info("Solr connection ok!" + str(solr_address))
        self.search_cnt = 0
        self.search_time = 0
        self.solr_search_time = 0
        self.solr_search_cnt = 0
        self.add_cnt = 0
        self.add_time = 0
        self.commit_cnt = 0
        self.commit_time = 0
        self.connection_limit = 10
        self.add_limit = 3000

    def setConnectLimit(self, limit):
        self.connection_limit = limit

    def getConnectLimit(self):
        return self.connection_limit

    def setAddLimit(self, cnt):
        self.add_limit = cnt
    
    def getAddLimit(self):
        return self.add_limit

    def close(self):
        if self.solrConnection <> None:
            try:
                self.solrConnection.realClose()
            except SolrException , e:
                logging.info(str(e))
        self.solrConnection = None

    def reconnect(self):
        logging.info("SOLR many error happend %d, reconnect begin", self.error_cnt)
        self.connect()
        if self.solrConnection <> None:
            logging.info("SOLR reconnect done")
            self.error_cnt = 0
        else:
            logging.warn("SOLR reconnect Wrong!")

    """
    connect 本质上是一种重连
    """
    def connect(self):
        self.close()
        time.sleep(2)
        for item in self.solr_address:
            try:
                self.solrConnection = Solr(item, False)
            except SolrException, e:
                self.solrConnection = None        
                logging.warn( str(e))
        if self.solrConnection == None:
            #reportNagios("Solr Connection Failed: "+ str(self.solr_address), NAGIOS_CRITICAL, NAGIOS_TYPE)
            """we never restart the engine for this error"""
            if self.error_cnt > self.getConnectLimit():
                logging.error("Solr connection Failed" + str(self.solr_address))

    """return a dic from doc_str
       the format of doc_str is name=value<tab>name=value<tab>...name=value
       return a dic which could used by solrpython to add document
    """
    def parseDoc(self, doc_str):
        doc_str = doc_str.strip()
        return_dic = {}
        info = doc_str.split("\t")
        for item in info:
            item_info = item.split("=")
            if len( item_info ) < 2:
                logging.warn("doc_str[%s] is not in good format, since item [%s] is not in .*=.* format"%(doc_str, item))
            else:
                if len(item_info) > 2:
                    item_info[1] = "=".join(item_info[1:])
                try:
                    return_dic[item_info[0]] = item_info[1].strip().decode("utf-8")
                except:
                    logging.warn("parse doc decoding wrong["+ doc_str + "]")
        if "PageTitle" in return_dic:
            try:
                tmp = " ".decode("utf-8") + return_dic["PageTitle"] +" ".decode("utf-8")
                (len_unicode, flag) = lenUnicode(tmp)
                if lenChinese(tmp) == 0 or  (len_unicode> 40 and flag == True):
                    logging.info("bad title too long or no chinese [%s]"%(return_dic["PageTitle"]))
                    del return_dic["PageTitle"]
            except Exception, e:
                logging.warn( str(e))
                logging.warn("decoding page tile wrong [%s]"%(doc_str))
        return return_dic

    def addTimeToQuery(self, query, last_time):
        current_time =  int(time.mktime(time.localtime()) )
        begin_time = current_time  - last_time 
        query = query 
        fq = "PublishTime:[" + str(begin_time) + " TO " +str(current_time) +  "]" 
        return (query, fq)


    """
    return a response
    TODO: 将时间加入搜索
    """
    def search(self, query, last_time="", query_terms="", **param):
        response = None
        json_result = ""
        self.testConn()
        if self.solrConnection <> None:
            try:
                start = time.time()
                if len(param) == 0:
                    (query,fqdata) = self.addTimeToQuery(query, last_time)
                    json_result = self.solrConnection.select(query, wt="json", qterms=query_terms, distrib="true", fq=fqdata, rows="2000")
                else:
                    json_result = self.solrConnection.select(query, **param)
                pass_time = time.time() - start
                #print "----------------Search-----------time: " + str(pass_time)
                self.search_cnt = self.search_cnt + 1
                self.search_time = self.search_time + pass_time
                json_format = json.loads(json_result)
                if SolrDocument.HEADER_TAG in json_format:
                    item = json_format[SolrDocument.HEADER_TAG]
                    if SolrDocument.QTIME_TAG in item:
                        tmp_search_time = int(item[SolrDocument.QTIME_TAG])
                        self.solr_search_cnt = self.solr_search_cnt + 1
                        self.solr_search_time = self.solr_search_time + tmp_search_time

                if SolrDocument.RESPONSE_TAG in json_format:
                    #try:
                    #    docs = DOCS
                    #except: 
                    #    pass
                    #if 'docs' in dir():
                    #    if DOCS in json_format[RESPONSE_TAG]:
                    #        return toUTF8ListDic(json_format[RESPONSE_TAG][DOCS] )
                    if 'docs' in json_format[SolrDocument.RESPONSE_TAG]:
                        return self.toUTF8ListDic(json_format[SolrDocument.RESPONSE_TAG]['docs'] )
                    return self.toUTF8ListDic(json_format[SolrDocument.RESPONSE_TAG] )
                else:
                    logging.warn("Solr Response wrong without %s [%s]"%(SolrDocument.RESPONSE_TAG, json_result))
                    return None
            except SolrException, e:
                logging.warn("Catch Search SolrException.")
                logging.warn( str(e) )
                self.error_cnt = self.error_cnt + 1
                self.reconnect()
                return None
            except Exception, e:
                logging.warn(e)
                logging.warn(" JSON FORMAT ERROR? " + json_result)
                self.reconnect()
                return None
            pass
        return None

    def toUTF8ListDic(self, res):
        for item in res:
            for i in item:
                if isinstance(item[i], types.UnicodeType)==True:
                    item[i] = unicode(item[i]).encode("utf-8")
        return res
    def toUnicodeListDic(self, res):
        for item in res:
            for i in item:
                if isinstance(item[i], types.StringType)==True:
                    item[i] = item[i].decode("utf-8")
        return res

    """
    dics is a array of dictionary

    """
    def addDocs(self, dics):
        self.testConn()
        if self.solrConnection <> None:
            try:
                start = time.time()
                self.solrConnection.add_many(dics, commit=False)
                self.add_cnt = self.add_cnt + len(dics)
                pass_time = time.time() - start

                self.add_time = self.add_time + pass_time
                self.doc_added_num = self.doc_added_num + len(dics)
                logging.info("Add A doc OK")
                if self.doc_added_num > self.getAddLimit(): #NUM_ADD_COMMIT:
                    self.commit()
                return True
            except SolrException, e:
                logging.warn("Catch addDocs SolrException.")
                logging.warn( str(e))
                self.error_cnt = self.error_cnt + 1
                self.reconnect()
                return False
            except Exception ,e:
                logging.warn("Catch addDocs Exception.")
                logging.error("add doc[[\n%s\n]]"%(traceback.format_exc()))
                
                logging.warn( str(e))
                self.error_cnt = self.error_cnt + 1
                self.reconnect()
                return False
                
        return False

    """
    return true, if commit ok

    """
    def commit(self):
        self.testConn()
        if self.solrConnection <> None:
            try:
                start = time.time()
                self.solrConnection.commit()
                self.commit_cnt = self.commit_cnt + 1
                pass_time = time.time() - start 
                self.commit_time = self.commit_time + pass_time
                #print "----------------commit-----------time: " + str(pass_time)
                #if pass_time > 0.05:
                #    print "Commit Time Long : %.4f"%(pass_time)
                
                tmp_num = self.doc_added_num
                self.doc_added_num = 0
                logging.info("commit done [%d] docs"%(tmp_num))
                return True
            except SolrException, e:
                logging.warn("Catch commit SolrException.")
                logging.warn( str(e))
                self.error_cnt = self.error_cnt + 1
                self.reconnect()
                return False
            except Exception, e:
                logging.warn("Catch commit Exception.")
                logging.warn( str(e))
                self.error_cnt = self.error_cnt + 1
                self.reconnect()
                return False
                
        else:
            return False

    def stat(self):
        avg_search = -1
        avg_add = -1
        avg_commit = -1
        solr_avg = -1
        if self.search_cnt > 0:
            avg_search = self.search_time *1./ self.search_cnt
            avg_search = avg_search * 1000
        if self.add_cnt > 0:
            avg_add = self.add_time * 1./self.add_cnt
            avg_add = avg_add * 1000
        if self.commit_cnt > 0:
            avg_commit = self.commit_time *1./self.commit_cnt
            avg_commit = avg_commit * 1000
        if self.solr_search_cnt > 0:
            solr_avg = self.solr_search_time *1./self.solr_search_cnt
        return "Search:%.2f Add:%.2f Commit:%.2f SolrSearch:%.2f"% ( avg_search , avg_add, avg_commit, solr_avg)

    def testConn(self):
        if self.solrConnection == None:
            self.error_cnt = self.error_cnt + 1
            self.reconnect()

if __name__ == "__main__":
    #solrdoc = SolrDocument(["http://192.168.23.46:25100/solr"])
    #data = solrdoc.search("百度", wt="json")
    solrdoc = SolrDocument(["http://192.168.23.103:6100/solr"])
    data = solrdoc.search("同花顺",wt="json",distrib="true",start=str(0),rows=str(20),de="false",fl="*",sort="PublishTime desc")
    print data
