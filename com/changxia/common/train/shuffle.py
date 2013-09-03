#!/usr/bin/python
#-*-coding:utf-8-*-
import random
import logging
import os
import sys
'''
该类根据概率值将数据随机划分到各个组。
用法
    shuffle = Shuffle( {"train":0.8, "test":0.2})
    切分文件
    files_dict = shuffle.shuffleFile("iris.data")
    其中files_dict 的key 是train，test，value是相应的文件名

    切分数组
    arrays_dict = shuffle.shuffleArray(data)
    其中arrays_dict 的key是train, test, value是相应的数组
   


'''

class Shuffle:

    '''
    probs 是dict， key是group的名字，value是该group的比例
    如：
       {train:0.8, test:0.2}

    '''
    def __init__(self, probs):
        self.group_data = self.initGroupMetaData(probs)
    

    def initGroupMetaData(self, probs):
        remain_prob = 1
        group_data = {}
        for item in probs:
            max = remain_prob
            min = remain_prob - probs[item]
            group_data[item] = (max, min)
            remain_prob = min
        return group_data

    '''
    随机返回一个group的名字
    '''
    def shuffleOneData(self):
        #get random data
        current_prob = random.random()
        for item in self.group_data:
            (max, min) = self.group_data[item]
            if current_prob <= max and current_prob > min:
                return item
    
    '''
    返回一个dict, key是组名，value是文件名
    '''
    def shuffleFile(self, filename):
        lines = open(filename, "r").readlines()
        filenames = {}
        #open files
        file_h_dict = {}
        for item in self.group_data:
            new_filename = filename + "." + item
            filenames[item] = new_filename
            file_h = open(new_filename, "w")
            file_h_dict[item] = file_h

        for item in lines:
            tag = self.shuffleOneData()
            file_h_dict[tag].write(item)

        #close files
        for item in file_h_dict:
            file_h_dict[item].close()

        return filenames
    
    '''
    返回一个dict, key是组名，value是数组
    '''
    def shuffleArray(self, data):
        #init arrarys
        shuffle_result = {}
        for item in self.group_data:
            shuffle_result[item] = []
        for item in data:
            tag = self.shuffleOneData()
            shuffle_result[tag].append(item)
        return shuffle_result



if __name__ == "__main__":
    shuffle = Shuffle( {"train":0.6, "test":0.2, "valid":0.2})
    filename = "iris.data"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    files_dict = shuffle.shuffleFile(filename)
    files_names = files_dict.values()
    for item in files_dict:
        print item,
        line_cnt = os.popen( "wc -l " + " "  + files_dict[item]).read().strip()
        print line_cnt
    data = []
    for x in xrange(1000):
        data.append( random.random())
    arrays_dict = shuffle.shuffleArray(data)
    for item in arrays_dict:
        print item, len( arrays_dict[item])
