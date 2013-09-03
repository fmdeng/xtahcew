#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
import hashlib
import os
import datetime
import logging
'''
基础的search
    maxSearch 最大匹配
    searchAll 全匹配
e.g.: see __main__


'''
class DictionarySearcher:
    def __init__(self, words_file="", key_index=0, meta_index=0):
        self.dictionary = {}
        if cmp(words_file, "") <> 0:
            self.loadWordsFile(words_file, key_index, meta_index)

    def maxSearch(self, text, coding, need_decode=True, need_add_info = True):
        '''
        @brief 返回最大匹配的相关信息
               返回信息中包含两个部分： 1、是匹配的的词典，词典内容格式：key是匹配内容，value（数组） 是匹配的位置(unicode的位置)。
                                           如果我们需要key的附属信息，那么value的第一个位置是附属信息
                                        2、文本长度 （历史遗留问题，没有用）
        @param coding text的编码
        @param need_decode 是否需要编码，如果是unicode，那么need_decode应该是False
        @param need_add_info 是否需要附属信息
        '''
        dictionary_return = {}
        if need_decode:
            coding = coding.lower()
            if cmp(coding, "gb2312") == 0 :
                coding = "gbk"
            try:
                text = text.decode(coding)
            except:
                logging.warn( "decoding wrong " + coding + "\n" )
                return (dictionary_return, 10000)
        list_of_text = list(text)
        start = 0
        span = 1
        while (start < len(list_of_text)):
            span = 1
            real_span = 0
            match_item = ""
            meta_info = None
            while 1==1:
                item_to_search = list_of_text[start:start + span]
                item_to_search ="".join(item_to_search)
                if item_to_search in self.dictionary:
                    if ( (self.dictionary[item_to_search]) <> None ):
                        real_span = span
                        match_item = item_to_search
                        meta_info = self.dictionary[item_to_search]
                else:
                    break #not found any more
                span = span + 1
                if ( start + span > len(list_of_text) ):
                    break ;
            if real_span == 0 :
                start = start + 1
            else:
                start = start + real_span
                if match_item in dictionary_return:
                    dictionary_return[match_item].append( str(start-real_span) )
                else:
                    if need_add_info:
                        dictionary_return[match_item] = [self.dictionary[match_item], str(start - real_span) ]
                    else:
                        dictionary_return[match_item] =[str(start - real_span) ]
        return (dictionary_return, len(list_of_text))

    def maxSearchEx(self, text, coding, need_decode=True):
        dictionary_return = {}
        if need_decode:
            coding = coding.lower()
            if cmp(coding, "gb2312") == 0 :
                coding = "gbk"
            try:
                text = text.decode(coding)
            except:
                logging.warn( "decoding wrong " + coding + "\n" )
                return (dictionary_return, 10000)
        list_of_text = list(text)
        start = 0
        span = 1
        while (start < len(list_of_text)):
            span = 1
            real_span = 0
            match_item = ""
            meta_info = None
            while 1==1:
                item_to_search = list_of_text[start:start + span]
                item_to_search ="".join(item_to_search)
                if item_to_search in self.dictionary:
                    if ( (self.dictionary[item_to_search]) <>None ):
                        real_span = span
                        match_item = item_to_search
                        meta_info = self.dictionary[item_to_search]
                        #dictionary_return[match_item]=meta_info
                else:
                    break #not found any more
                span = span + 1
                if ( start + span > len(list_of_text) ):
                    break ;
            if real_span == 0 :
                start = start + 1
            else:
                start = start + real_span
                if match_item in dictionary_return:
                    dictionary_return[match_item].append(str(start-real_span))
                else:
                    dictionary_return[match_item] = [str(start - real_span)]
        return (dictionary_return, len(list_of_text))



    def searchAll(self, text, coding, need_decode=True, need_add_info=True):
        '''
        @brief 返回全匹配的相关信息
               返回信息中包含两个部分： 1、是匹配的的词典，词典内容格式：key是匹配内容，value（数组） 是匹配的位置(unicode的位置)。
                                           如果我们需要key的附属信息，那么value的第一个位置是附属信息
                                        2、文本长度 （历史遗留问题，没有用）
        @param coding text的编码
        @param need_decode 是否需要编码，如果是unicode，那么need_decode应该是False
        @param need_add_info 是否需要附属信息
        '''

        dictionary_return = {}
        if need_decode:
            coding = coding.lower()
            if cmp(coding, "gb2312") == 0 :
                coding = "gbk"
            try:
                text = text.decode(coding)
            except:
                logging.warn("decoding wrong " + coding + "\n" )
                return (dictionary_return, 10000)
        list_of_text = list(text)
        start = 0
        span = 1
        while (start < len(list_of_text)):
            span = 1
            real_span = 0
            match_item = ""
            meta_info = None
            while 1==1:
                item_to_search = list_of_text[start:start + span]
                item_to_search ="".join(item_to_search)
                if item_to_search in self.dictionary:
                    if ( (self.dictionary[item_to_search]) <> None ):
                        real_span = span
                        match_item = item_to_search
                        meta_info = self.dictionary[item_to_search]
                        pos = start + real_span
                        if match_item in dictionary_return:
                            dictionary_return[match_item].append( str(pos-real_span) )
                        else:
                            if need_add_info:
                                dictionary_return[match_item] = [self.dictionary[match_item], str(pos - real_span) ]
                            else:
                                dictionary_return[match_item] =[str(pos - real_span) ]

                else:
                    break #not found any more
                span = span + 1
                if ( start + span > len(list_of_text) ):
                    break ;
            start = start + 1
        return (dictionary_return, len(list_of_text))

    def addKey(self, key, feature=""):
        '''
        @param key 需要匹配的字符串
        @param feature 附属信息，如果附属信息为空，那么key本身就是附属信息
        '''
        if cmp(key, "") == 0:
            return
        if cmp(feature, "") == 0:
            feature = key
        key = key.decode("utf-8")
        feature = feature.decode("utf-8")
        feature = feature.strip()
        feature_info = feature
        self.dictionary[key] = feature_info
        keys = list(key)
        length_of_line_info = len(keys)
        for i in xrange(1, length_of_line_info):
            new_key = "".join(keys[:i])
            if new_key in self.dictionary :
                pass
            else:
                self.dictionary[new_key] = None

    def loadWordsFile(self, words_file, key_index, meta_index, split_char=' '):
        '''
        @param words_file 词汇文件
        @param split_char 词汇文件按照该字符进行列的切分
        @param key_index  列号为key_index的内容作为匹配词汇
        @param meta_index 附属信息的列号
        @brief 加载匹配词汇
        '''
        input_file = open ( words_file , "r")
        lines = input_file.readlines()
        for line in lines:
            try:
                line = line.decode("utf-8") #every word is in the format of utf-8
            except Exception:
                continue
            line = line.strip()
            line_info = line.split(split_char)
            length_of_line_info = len(line_info) 
            if length_of_line_info <= key_index  or length_of_line_info <= meta_index :
                logging.warn( "[error] Breaking Line " + line )
                continue
            meta_info = line_info[meta_index]
            key = line_info[key_index]
            self.dictionary[key] = meta_info

            meta_info = None
            keys = list(key)
            length_of_line_info = len(keys)
            for i in xrange(1, length_of_line_info):
                new_key = "".join(keys[:i])
                if new_key in self.dictionary :
                    pass
                else:
                    self.dictionary[new_key] = meta_info
        input_file.close()



if __name__=="__main__":
    s="中国保监会巴巴保监会"
    dic_search = DictionarySearcher()
    dic_search.addKey("巴巴")
    dic_search.addKey("和国", "ok right")
    dic_search.addKey("保监会", "1")
    dic_search.addKey("保监", "1")
    (result, len_txt) = dic_search.searchAll(s, "utf-8", True, False)
    for item in result:
        #匹配的key
        print item.encode("utf-8")  + "\t" ,
        #匹配的位置
        print " ," .join( result[item] )

