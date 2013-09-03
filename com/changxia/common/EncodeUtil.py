#!/usr/bin/env python
#-*-coding:utf-8-*- 
import re
import urlparse
"""
字符转换的一些通用函数
"""
def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False

def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar<=u'\u0039':
         return True
    else:
        return False

def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False

def is_hexin_whitespace(uchar):
    """判断一个unicode是否是搜牛特殊空白字符"""
    if uchar >= u'\ue000' and uchar <= u'\ue0ff':
        return True
    return False

def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False

def B2Q(uchar):
    """半角转全角"""
    inside_code=ord(uchar)
    if inside_code<0x0020 or inside_code>0x7e:      #不是半角字符就返回原来的字符
        return uchar
    if inside_code==0x0020: #除了空格其他的全角半角的公式为:半角=全角-0xfee0
        inside_code=0x3000
    else:
        inside_code+=0xfee0
    return unichr(inside_code)

def Q2B(uchar):
    """全角转半角"""
    inside_code=ord(uchar)
    if inside_code==0x3000:
        inside_code=0x0020
    else:
        inside_code-=0xfee0
    if inside_code<0x0020 or inside_code>0x7e:      #转完之后不是半角字符返回原来的字符
        return uchar
    return unichr(inside_code)

def stringQ2B(ustring):
    """把字符串全角转半角"""
    return "".join([Q2B(uchar) for uchar in ustring])

def uniform(ustring):
    """格式化字符串，完成全角转半角，大写转小写的工作"""
    return stringQ2B(ustring).lower()


def lenChinese(string):
    '''计算中文字符的长度'''
    len = 0
    for item in string:
        if is_chinese(item):
            len = len + 1
    return len

def lenUnicode(string, consider_ascii=True):
    '''计算文本长度，连续的英文和数字记为1'''
    len = 0
    has_chinese = False
    pre_other = True
    for item in string:
        if is_chinese(item):
            len = len + 1
            has_chinese = True
            pre_other = True
        if is_alphabet(item) or is_number(item):
            if pre_other == True:
                len = len + 1
                pre_other = False
        if is_other(item):
            pre_other = True
    return (len, has_chinese)


if __name__=="__main__":
    #test Q2B and B2Q
    #for i in range(0x0020,0x007F):
    #    print Q2B(B2Q(unichr(i))),B2Q(unichr(i))
    #test uniform
    ustring=u'中国 人名ａ高频Ａ'
    ustring="．".decode("utf-8")
    ustring=uniform(ustring)
    print ustring.encode("utf-8")
