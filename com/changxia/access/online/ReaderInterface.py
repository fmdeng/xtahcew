#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
sys.path.append("../../")
from common.log.logger import *

class ReaderInterface(object):

    '''
    @初始化读取对象
    '''
    def open(self, config_dict):
        raise NotImplementedError, "Cannot call abstract method open in ReaderInterface"
        pass

    '''
    @param result_dict，存放获得的结果
           每一个元素是一个doc，doc是一个字典
    @pram next_meta, next_meta存储了本次读取结果的参数，当函数返回的时候
          其内容将被更改，为下一轮读取内容做好准备
    @return 返回True， 还可以继续获得结果， False没有结果
    '''
    def next(self, result_dict=[], next_meta={}):
        raise NotImplementedError, "Cannot call abstract method next in ReaderInterface"
        pass

    '''
    @brief 判断是否读完了数据
    @return True, 文件已经读完了，False 还没有读完
    '''
    def ieof(self):
        raise NotImplementedError, "Cannot call abstract method ieof in ReaderInterface"
        pass

    '''
    @brief 返回目前读取的位置
    @return 读取位置
    '''
    def getPos(self):
        raise NotImplementedError, "Cannot call abstract method getPos in ReaderInterface"
        pass


    '''
    @return 返回平均读取文档的时间
    '''
    def getAverageTime(self):
        raise NotImplementedError, "Cannot call abstract method getAverageTime in ReaderInterface"
        pass

    def setbad(self):
        self.is_bad = True

    def setgood(self):
        self.is_bad = False
    '''
    open 成功后 该函数为True
    打开失败或者读取失败该函数为False
    '''
    def isGood(self):
        return self.is_bad == False
