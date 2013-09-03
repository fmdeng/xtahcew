#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
sys.path.append("../../")
import urllib
import urllib2
import re
from common.log.logger import *
from ReaderInterface import *
from OnlineReaderUtil import *
from common.TimeHelper import *
import time
import logging
import traceback
'''
给定query，按照时间顺序获得online某一个channel的内容
eg:
   参考main 下的说明
'''
class OnlineTimeReader(ReaderInterface):
    
    '''
    @param config_dict: 配置信息
           config_dict['url'] online url
           config_dict['channel'] online channel
              取值 参考http://172.20.0.52/wiki/index.php/SFE%E6%8E%A5%E5%8F%A3
           config_dict['other_param'] online 一些搜索参数
              取值 参考http://172.20.0.52/wiki/index.php/SFE%E6%8E%A5%E5%8F%A3
           config_dict['solr'] 定义了solr的数据项(如contentsize, UID)，作为返回结果
           config_dict['desc'] 定义了desc的数据项(如title content)，作为返回结果
           config_dict['time_start'] 搜索起始时间
           config_dict['time_end'] 搜索结束时间
           config_dict['q'] 搜索query
           config_dict['every_time_cnt'] 每次搜索返回的结果
           config_dict['max_number'] 最多取多少结果
           config_dict['offset'] 从第几个结果开始取
    @return 打开失败返回False， 否则True
    '''
    def open(self, config_dict, st="1"):
        self.setbad()
        try:
            if "url" not in config_dict or \
               "channel" not in config_dict or \
               "solr" not in config_dict or \
               "time_start" not in config_dict or \
               "time_end" not in config_dict or \
               "q" not in config_dict:
                raise OnlineReaderException("q,url,channel,solr,time_start,time_end \
                is not given when initializing Reader")
            self.url = config_dict["url"]
            self.query = config_dict["q"]
            self.channel = config_dict["channel"]
            self.solr_meta = config_dict["solr"]
            self.solr_meta["UID"] = ""
            self.desc_meta = {}
            if "desc" in config_dict:
                self.desc_meta = config_dict["desc"]
            self.time_start = config_dict["time_start"]
            self.time_end = config_dict["time_end"]
            self.every_time_cnt = 200
            if "every_time_cnt" in config_dict:
                self.every_time_cnt = int (config_dict['every_time_cnt'] )
            self.max_number = 200
            if 'max_number' in config_dict:
                self.max_number = int(config_dict['max_number'])
            self.base_param = {}
            if "other_param" in config_dict:
                self.base_param = config_dict['other_param']
            self.base_param['tr'] = '6' #用秒自定义时间
            self.base_param['st']= st   #默认按照publishtime进行排序
            self.base_param['nd'] = '0'
            self.base_param['tid'] = self.channel
            self.base_param['q'] = self.query
            self.base_param['sm'] = "%s,%s"%( str(self.time_start), str(self.time_end))
            self.need_desc = len(self.desc_meta) <> 0
            self.desc_reader = DescReader(self.url)
            self.is_end = False
            self.offset = 0
            if 'offset' in config_dict:
                self.offset = int(config_dict['offset'])
            self.org_offset = self.offset
            self.start_time = time.time()
            self.setgood()
            return True
        except:
            logging.error("open reader wrong " + traceback.format_exc())
            self.setbad()
            return False
    '''
    @param result_dict 存放读取结果，其中每一个元素的类型是字典，key是config_dict中solr和desc里key
    @param next_meta 存放的是下次读取信息的元信息，包括起始位置和长度，第一次调用的时候next_meta设置为{}
    '''
    def next(self, result_dict=[], next_meta={}):
        try:
            if len(next_meta) == 0:
                next_meta["start"] = 0
                next_meta["length"] = self.every_time_cnt
                self.start_time = time.time()
            logging.info(next_meta)
            #准备获取数据
            param = self.base_param
            param["s"] = str(next_meta["start"])
            param["c"] = str(next_meta["length"])
            param["nw"] = str(int(next_meta["start"]) + int(next_meta["length"]) )
            content = OnlineReaderUtility.post(self.url, param)
            content = OnlineReaderUtility.trimcontent(content)
            OnlineReaderUtility.getAllItems(content, self.solr_meta, result_dict)
            len_result = len(result_dict)
            self.offset += len_result

            if self.need_desc:
                for index in xrange(len_result): 
                    if "UID" in result_dict[index]:
                        uid = result_dict[index]['UID']
                        if self.channel == "report":
                            self.channel="report_pdf"  #TODO just for notice
                        data = self.desc_reader.getTitleContent(uid, self.channel, self.desc_meta)
                        if data <> None:
                            for e in data:
                                result_dict[index][e] = data[e]

            if len_result  == 0 or self.offset-self.org_offset >= self.max_number:
                if len_result == 0:
                    self.is_end = True
                return False
            next_meta["start"] = next_meta["start"] + next_meta["length"]
            return True
        except:
            logging.error("read data wrong " + traceback.format_exc())
            self.setbad()
            return False

    def ieof(self):
        return self.is_end
        pass


    def getPos(self):
        return self.offset
        pass

    def getAverageTime(self):
        pass_time = time.time() - self.start_time
        result_cnt = self.offset - self.org_offset
        if result_cnt == 0:
            return 0
        return pass_time/(1. *result_cnt)
        pass



if __name__ == "__main__":
    #设置搜索时间
    time_helper = TimeHelper()
    time_start = time_helper.getSecondsFromDateTime("2011-03-01 00:00")
    time_end = time.mktime(time.localtime()) 
    config_dict = {"url":"http://192.168.201.87:8888/search", \
                   "channel":"report",  \
                   "other_param":{"sde":"0"}, \
                   "solr":{ "UID":"", "contentsize":"1"},\
                   "desc":{"title":"", "content":""}, \
                   "time_start": int(time_start), \
                   "time_end": int(time_end),\
                   "max_number":500,\
                   "q": "烟台万华" }
    online_news_reader = OnlineTimeReader()
    online_news_reader.open(config_dict)
    result_dict = [] #存放结果 每个结果是一个字典，key是 solr 和 desc指定的内容
    next_meta = {}
    while (online_news_reader.next(result_dict, next_meta)):
        for item in result_dict:
            for e in item:
                print e, item[e]
        result_dict=[]
    if len(result_dict) <> 0:
        for item in result_dict:
            for e in item:
                print e, item[e]
    print time_start
    print time_end
    print online_news_reader.getAverageTime()
    print online_news_reader.getPos()
    print online_news_reader.ieof()
    print online_news_reader.isGood()
