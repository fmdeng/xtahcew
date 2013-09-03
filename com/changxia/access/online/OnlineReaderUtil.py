#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
sys.path.append("../../")
import urllib
import urllib2
import re
from common.log.logger import *
from ReaderInterface import *
'''
读取online的相关函数
参考：
http://172.20.0.52/wiki/index.php/SFE%E6%8E%A5%E5%8F%A3
获得相关的参数信息
'''
class OnlineReaderException(Exception):
    def __init__( self, msg ):
        Exception.__init__(self, 'OnlineReaderException[%s]'%msg)

class OnlineReaderUtility:

    '''
    @param data a dict
    @param url, online url
    @return web page from online
    '''
    @staticmethod
    def post( url, data):
        data = urllib.urlencode(data)
        search_url =  url + "?" + data 
        req = urllib2.Request(search_url)
        req.set_proxy("172.20.201.254:3128", "http")
        file_h = urllib2.urlopen(req)
        logging.debug(search_url)
        search_url = search_url
        line = file_h.read()
        return line

    '''
    修剪获得的数据
    '''
    @staticmethod
    def trimcontent(lines):
        lines = re.sub(r'\r', " ", lines)
        lines = re.sub(r'\n', " ", lines)
        lines = re.sub(r'\s+', " ", lines)
        return lines

    '''
    @param content online 返回的一条数据的内容
    @param tag  一条数据的某一项内容，如UID URL
    @return 返回一项内容
    '''
    @staticmethod
    def getMeta( content ,tag, defalut="NONENONE"):
        elements = re.findall(r'<%s>(.*)<\/%s>'%(tag, tag), content)
        if len(elements) > 0:
            return elements[0]
        else:
            return defalut


    '''
    @brief 抽取搜索结果
    @param meta 每条结果中要的内容
    @return  [ item, item,...], item= dict{}
    '''
    @staticmethod
    def getAllItems(content, meta, result_dict, pattern_start="<item type", pattern_end="</item>"):
        items = re.findall(r'%s(.*?)%s'%(pattern_start, pattern_end), content)
        #print len(items)
        for item in items:
            dict_tmp = {}
            for tag in meta.keys():
                dict_tmp[tag] = OnlineReaderUtility.getMeta(item, tag, meta[tag])
            result_dict.append(dict_tmp)
        return result_dict

class DescReader(object):

    def __init__(self, url):
        self.url = url

    def getTitleContent(self, uid, dtype, meta={"title":"", "content":""}):
        content = self.getDesc(uid, dtype)
        data = []
        data = OnlineReaderUtility.getAllItems(content, meta, data, "<desc>", "</desc>")
        if len(data) == 0:
            return None
        else:
            if 'content' in  data[0]:
                data[0]['content'] =self.getContent(data[0]['content'] )
            return data[0]
        return None

    def getContent(self, content):
        begin=u'\ue086'
        end=u'\ue087'
        paragraph_pattern = "(".decode("utf-8") + u'\ue008' + "|".decode("utf-8") + u'\e009' + ")".decode("utf-8")
        pattern = begin + "(.*?)".decode("utf-8") + end
        content = content.decode("utf-8")
        #elements = re.findall(pattern, content)
        elements = self.findSegment(content,begin,end)
        if len(elements) <> 0:
            data = ("\n".decode("utf-8").join(elements))
            data = re.sub(paragraph_pattern, "\n", data)
            ret_content = data
        else:
            ret_content = content
        ret_content = self.rmNoncharUnicode(ret_content)
        return ret_content.encode("utf-8")
    def findSegment(self,text,SegmentTypeBegin,SegmentTypeEnd):
        ret_list = []
        begin_list = []
        for m in re.finditer(SegmentTypeBegin, text,re.UNICODE):
            begin_list.append(m.start())
        end_list = []
        for m in re.finditer(SegmentTypeEnd, text,re.UNICODE):
            end_list.append(m.start())
        for begin in begin_list:
            right_end = -1
            for end in end_list:
                if end > begin:
                    right_end = end
                    break
            if right_end != -1 and right_end > begin + 1:
                ret_list.append(text[begin:right_end])
        return ret_list
    def rmNoncharUnicode(self,line):
        new_line = "".decode("utf-8")
        for uchar in line:
            if uchar >= u'\uE000' and uchar<=u'\uE0FF':
                continue
            new_line += uchar
        return new_line

    def getDesc(self,uid, dtype):
        data = {}
        data["duid"] = uid
        data["dtype"] = dtype
        data["q"] = "0"
        data["tid"] = "desc"
        content = OnlineReaderUtility.post(self.url, data)
        return OnlineReaderUtility.trimcontent(content)



if __name__ =="__main__":
    desc_reader = DescReader("http://192.168.201.87:8888/search")
    #data = desc_reader.getTitleContent("47d14b59e31acbe", "news")
    #data = desc_reader.getTitleContent("fb3d2a2cf5709759", "report_pdf")
    data = desc_reader.getTitleContent("5db4026cac309ade", "news")
    print data["title"]
    print data['content']
