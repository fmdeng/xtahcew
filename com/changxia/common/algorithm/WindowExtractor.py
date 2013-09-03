#/usr/bin/python
#-*-coding:utf-8-*-

import os,sys
sys.path.append("../..")
import logging
from common.DictionarySearcher import *
from common.EncodeUtil import *
'''
first version: taozhiwei@myhexin.com
算法介绍： 
    输入：
        1）一组中文字，或者词。假设是（A, B,C)。
        2）窗口大小, 假设是 n
        3）一段文本, 假设是 s
    输出: 以 A、B、或者C为中心，在原有的文本中，左右至少增加一个中文字，最多增加n个中文字

    例子:
    word_list = ["同花顺", "大智慧"]
    window = 3
    window_extractor = WindowExtractor(word_list, window)
    s="一般用户用同花顺好一点，界面比较人性"
    patterns = window_extractor.extractPattern(s)

    patterns是一个数组(utf-8):

    同花顺好一点
    用户用同花顺好一
    用户用同花顺
    户用同花顺好一
    用同花顺
    用同花顺好
    用同花顺好一
    用户用同花顺好
    户用同花顺好
    同花顺好一
    同花顺好
    户用同花顺
    用同花顺好一点
    户用同花顺好一点
    用户用同花顺好一点

'''
class WindowExtractor:

    def __init__(self, word_list, window):
        self.dic_search = DictionarySearcher()
        for item in word_list:
            self.dic_search.addKey(item, "0")
        self.window = window
        self.block_chars_dict = {}
        self.block_chars_dict["。".decode("utf-8")] = 1
        self.block_chars_dict["?".decode("utf-8")] = 1
        self.block_chars_dict["\n".decode("utf-8")] = 1
        self.block_chars_dict["\r".decode("utf-8")] = 1
        self.block_chars_dict["？".decode("utf-8")] = 1

    def setBlockChar(self, char):
        self.block_chars_dict[char.decode("utf-8")] = 1

    def extractPattern(self, s):
        '''
        以match的词为中心，左右移动self.window 个词
        '''
        pattern_result = []
        s_unicode = s.decode("utf-8")
        content_length = len(s_unicode) ;
        (result, len_txt) = self.dic_search.maxSearch(s, "utf-8")
        for item in result:
            match_length = len(item)
            for index in result[item][1:]:
                index = int(index)
                (start, end ) = self.getWinow( index,  content_length, match_length, s_unicode)
                '''generate pattern'''
                result_range = {}
                self.generatePattern(index, match_length, start, end, result_range, s_unicode)
                for item in result_range:
                    if result_range[item] == 1:
                        (start, end) = item.split("-") 
                        start = int(start)
                        end = int(end)
                        pattern_result.append( s_unicode[start:end+1])
                pass
        return pattern_result

    def generatePattern(self, index, match_length, start, end, result_dict, content):
        '''
        递归函数，穷举组合
        '''
        if start >= index and end <= index + match_length - 1:
            return
        #输出自身
        key = "%d-%d"%(start, end)
        if key in result_dict:
            return
        try:
            if is_chinese(content[start]) and is_chinese(content[end]):
                result_dict[key] = 1
            else:
                result_dict[key] = 0
            #左递归
            while start < index:
                #start -> find the first chinese
                if is_chinese(content[start + 1] ):
                    self.generatePattern( index, match_length, start + 1, end, result_dict, content)
                    break
                start = start + 1
            #右递归
            while end > index + match_length -1:
                #end -> find the first chinese
                if is_chinese(content[end -1]):
                    self.generatePattern( index, match_length, start, end -1, result_dict, content)
                end -= 1
        except:
            return

    def getWinow(self, index, length, match_length, content):
        start = index
        window = self.window
        for i in xrange(index):
            new_index = index -i -1
            if new_index < 0:
                break
            if content[new_index] in self.block_chars_dict:
                break
            if is_chinese(content[new_index]):
                window -= 1
            start = new_index
            if window == 0:
                break
        end = index +  match_length -1
        window = self.window
        for i in xrange(index+match_length, length):
            new_index = i
            if new_index < 0:
                break
            if content[new_index] in self.block_chars_dict:
                break
            if is_chinese(content[new_index]):
                window -= 1
            end = new_index
            if window == 0:
                break
        return (start, end)


if __name__ == "__main__":
    word_list = ["同花顺", "大智慧"]
    window = 3
    window_extractor = WindowExtractor(word_list, window)
    s="一般用户用同花顺好一点，界面比较人性"
    patterns = window_extractor.extractPattern(s)
    for item in patterns:
        print item
