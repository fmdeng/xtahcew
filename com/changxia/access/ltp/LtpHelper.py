#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
import os
import logging
import re
import urllib2
import urllib
import redis
import logging
import json
sys.path.append("../..")
LTPSERVER_IP="192.168.23.32"
LTPSERVER_PORT="8002"
LTP_STOPWORD="data/stopwords.txt"
from common.strutil import *
from common.ltpclient.LtpPyClient import *
valid_tag= ["a","b","d","i","j","k","m","nd","q","v","ws"]
VALID_TAG = set(valid_tag)
class LtpHelper:

    def __init__(self,ip=LTPSERVER_IP,port=LTPSERVER_PORT,stopword=LTP_STOPWORD):
        if stopword == None:
            self.ltpClient = SeggerClient([(ip,port)])
        else:
            self.ltpClient = SeggerClient([(ip,port)],stopword)
        self.ltpClient.connect()
    
    def __del__(self):
        pass

    # get info from ltp string 
    def getSegmentInfo(self,result_str,valid_tag=None):
        word_list = []
        tmp_list1 = result_str.split(" ")
        for item1 in tmp_list1:
            if len(item1) <= 4 or item1.find(":") == -1:
                continue
            tmp_list2 = item1.rsplit("/",1)
            word = tmp_list2[0]
            tmp_list3 = tmp_list2[1].split(":")
            if valid_tag == None or (tmp_list3[3] in valid_tag): 
                word_list.append((word,tmp_list3[0],tmp_list3[1],tmp_list3[3]))
        return word_list

    def getSegment(self,content,param1,param2,param3):
        if param1 == None:
            (a,b,flag) = self.ltpClient.getMixSegment(content)
        else:
            (a,b,flag) = self.ltpClient.getMixSegment(content,param1,param2,param3)
        return (a,b,flag)

    def extractValidWord(self, string, valid_tag=VALID_TAG):
        result_list = self.getSegmentInfo(string,valid_tag)
        inx = 0
        pos_map = {}
        while inx < len(result_list):
            cur_item = result_list[inx]
            (word, begin, str_len, pos_tag) = cur_item
            inx +=1
            pos_map[word] = pos_tag
        return pos_map

if __name__ == '__main__':
    rephase = LtpHelper()
    (a,b,flag)=rephase.getSegment("在酒鬼酒没有爆出“塑化剂丑闻”之前，这场危机一直在暗处涌流而没有公之于众，酒业协会无非是担忧，一旦将信息公>开，白酒业将遭到重创",1,0,0)
    print a
    rephase.extractValidWord(b)
