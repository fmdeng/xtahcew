#!/usr/bin/env python
#-*-coding:utf-8-*-

import re
import curses.ascii
import random

# find surround string
SENTENCE_DIVIDER=[',','，',"？","。","：","！","；"," ","\""]
SENTENCE_END=['。','？',"！","\n","；",";"]
SENTENCE_END2=['。','？',"！"]
def findSurround(bPri,pos,pattern_len,content_uni):
    content_len = len(content_uni)
    if bPri:
        start = pos + pattern_len
        end = content_len
        inc = 1
        if start >= end:
            return None
    else:
        start = pos - 1
        end = -1
        inc = -1
        if start <= end:
            return None
    index = start
    while index != end and index >= 0 and index < content_len:
        check_char = content_uni[index].encode("utf-8")
        if check_char in SENTENCE_DIVIDER:
            index -= inc
            break
        index += inc
    if index < 0:
        index = 0
    if index >= content_len:
        index = content_len -1
    if (bPri and index < start) or ((not bPri) and start < index):
        return None

    if start < index:
        return content_uni[start:index+1].encode("utf-8")
    else:
        return  content_uni[index:start+1].encode("utf-8")
def splitFiles(incTxt,line_len,divCnt):
    if line_len % divCnt != 0:
        lineCnt = line_len / divCnt + 1
    else:
        lineCnt = line_len / divCnt
    os.system("split -d -l %d %s"%(lineCnt,os.path.basename(incTxt)))
def splitSentence(line, sentence_end=SENTENCE_END):
    sen_list = []
    sen_list.append(line)
    for divide in sentence_end:
        new_list = []
        for sen in sen_list: 
            tmp_list = re.split(divide,sen)
            new_list += tmp_list
        sen_list = new_list
    return sen_list
# char basic function
def isAlphaOrNum(string):
    for c in string:
        if (not c.isalpha()) and (not c.isdigit()):
            return False
    return True
def hasNum(string):
    for c in string:
        if (c.isdigit()):
            return True
    return False
def hasBlank(string):
    for c in string:
        if (curses.ascii.isblank(c)):
            return True
    return False
def isFullAlphaOrNum(string):
    for c in string:
        if (not c.isalpha()) and (not c.isdigit()):
            return False
    return True

def isFullDigit(string):
    for c in string:
        if (not c.isdigit()):
            return False
    return True

def isSingleAlpha(string):
    return (len(string) == 1 and string[0].isalpha())

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False

def removeUChar(string, re_char):
    ret = "".decode("utf-8")
    for char in string:
        if char != re_char:
            ret += char
    return ret
def removeUChars(string, re_char):
    ret = "".decode("utf-8")
    for char in string:
        if not char in re_char:
            ret += char
    return ret

def replaceConChar(string):
    newln = ""
    for ch in string:
        if not curses.ascii.iscntrl(ch):
            newln += ch
    return newln
def replaceNonWord(string):
    newln = ""
    for ch in string:
        if curses.ascii.iscntrl(ch):
            continue
        if curses.ascii.isblank(ch):
            continue
        newln += ch
    return newln

def getRandomStr(slen=8,charsets=None):
    if charsets == None or charsets == "":
        charsets = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIGKLMNOPQRSTUVWXYZ";
    return "".join(random.sample(charsets,slen))

def rmNoncharUnicode(line):
    new_line = "".decode("utf-8")
    for uchar in line:
        if uchar >= u'\uE000' and uchar<=u'\uE0FF':
            continue
        new_line += uchar
    return new_line
if __name__ == '__main__':
    splitFiles("person.log",122261,10)
