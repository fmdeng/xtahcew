#/usr/bin/python
#-*-coding:utf-8-*-
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from hbasethrift import Hbase
from hbasethrift.ttypes import *
#from OnlineTitleContentGetter import *
import logging
import re

class HbaseClient():
    
    HBASE_IP='192.168.23.35'
    HBASE_PORT=9090

    def __init__(self, server=HBASE_IP, port=HBASE_PORT):
        ''' 
        Exceptions:
            raise ConnectionError exception when connection error
        '''
        try:
            transport = TSocket.TSocket(server, port)
            self.transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
            self.client = Hbase.Client(protocol)
            self.transport.open()
        except Exception,e:
            logging.warn("can not connect to hbase! %s" %str(e))
    
    def __del__(self):
        self.transport.close()
    
    def getRow(self, tablename, row):
        ''' get row  from  tablename '''
        ret = ""
        try:
            ret = self.client.getRow(tablename, row)
        except Exception,e:
            logging.warn("get row from hbase wrong! %s" %str(e))
        return ret
    
    def getValue(self, tablename, row, colum):
        ''' get colun from row in tablename '''
        s = []
        try:
            s = self.client.get(tablename, row, colum)
        except Exception,e:
            logging.warn("get colum form hbase wrong! %s" %str(e))
            return ""
        if len(s) > 0:
            return s[0].value
        else:
            return ""

    def getTextContentEntity(self, tablename, row):
        '''  get textContent from Description:PageBody '''
        return self.getSegEntityFromBody(tablename, row, u'\uE086', u'\uE087')


    def getSegEntityFromBody(self, tablename, row, SegmentTypeBegin, SegmentTypeEnd):
        ''' get need entity from Description:PageBody which SegmentType is given '''
        s = self.getValue(tablename, row, "Description:PageBody")
        if s == "":
            return ""
        #reslist = re.findall("%s(.*?)%s" %(SegmentTypeBegin, SegmentTypeEnd),s.decode("utf-8"),re.UNICODE)
        reslist = self.findSegment(s,SegmentTypeBegin,SegmentTypeEnd)
        if len(reslist) == 0:
            return ""
        return "\n".join(reslist)

    def getTitleContent(self, row, tablename='OnlineNewsTest'):
        ''' get textContent from PageBody and PageTitle which tablename is OnlineNewsTest or OnlineNews'''
        content = self.getTextContentEntity(tablename, row)
        content = self.rmNoncharUnicode(content)
        title = self.getValue(tablename, row, "Description:PageTitle")
        return (title, content)

    def rmNoncharUnicode(self,line):
        new_line = "".decode("utf-8")
        for uchar in line:
            if uchar >= u'\uE000' and uchar<=u'\uE0FF':
                continue
            new_line += uchar
        return new_line

    def findSegment(self,s,SegmentTypeBegin,SegmentTypeEnd):
        text = s.decode("utf-8")
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
            

if __name__ == "__main__":
    hc = HbaseClient("192.168.23.29",9090)
    #print hc.getRow('Top500_News_inte_test', '100001ead9a6d1c')
    #print hc.getValue('OnlineNewsTest', '10000057dc14c2c2', "Description:PageBody")
    #print hc.getTextContentEntity('OnlineNewsTest', '47d14b59e31acbe')
    #print hc.getValue('Top500_News_inte_test', '100001ead9a6d1c', "Content:HTTPBody")
    #print "--------------------"
    #print hc.getTextContentEntity('Top500_News_inte_test', '100001ead9a6d1c')
    content = hc.getValue( "IndustryReport_dev", "36189", "Content:paragraphs")
    print content
