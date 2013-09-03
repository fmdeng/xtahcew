#!/usr/bin/python
#-*-coding:utf-8-*-

import sys
import os
import commands
from hadoop_conf import *
from conf.HexinConfiguration import *
#command = "hadoop dfs -ls /user/hexinnell"
# mkdir 
def mkHdfsDir(hdfs_dir):
    command = "hadoop dfs -mkdir %s"%(hdfs_dir)
    (status, output) = commands.getstatusoutput(command + "  2>/dev/null")
    return status
# lsdir 
def lsHdfsDir(hdfs_dir):
    command = "hadoop dfs -ls %s"%(hdfs_dir)
    (status, output) = commands.getstatusoutput(command + "  2>/dev/null")
    return output
# read file 
def readHdfsFile(hdfs_dir,file_name):
    command = "hadoop dfs -cat %s/%s"%(hdfs_dir,file_name)
    (status, output) = commands.getstatusoutput(command + "  2>/dev/null")
    return output
# put file 
def putHdfsFile(hdfs_dir,target_file,local_file):
    command = "hadoop dfs -put %s %s/%s"%(local_file,hdfs_dir,target_file)
    (status, output) = commands.getstatusoutput(command + "  2>/dev/null")
    return status
# get file 
def getHdfsFile(hdfs_dir,target_file,local_file):
    command = "hadoop dfs -get %s/%s %s"%(hdfs_dir,target_file,local_file)
    (status, output) = commands.getstatusoutput(command + "  2>/dev/null")
    return status

# save data dir
def saveData(conf_str):
    conf = HexinConfiguration(conf_str)
    hdfs_dir = conf.getProperty("Configuration.hdfs_dir.value")
    local_data_dir = conf.getProperty("Configuration.local_data_dir.value")
    data_list = []
    node_list = conf.getNodeList("Configuration.restoreDataList")
    for node in node_list:
        data_list.append(node["value"])
    mkHdfsDir(hdfs_dir)
    for data_file in data_list:
        putHdfsFile(hdfs_dir,data_file,local_data_dir+"/"+data_file)
# resotreData
def restoreData(conf_str):
    conf = HexinConfiguration(conf_str)
    hdfs_dir = conf.getProperty("Configuration.hdfs_dir.value")
    local_data_dir = conf.getProperty("Configuration.local_data_dir.value")
    data_list = []
    node_list = conf.getNodeList("Configuration.restoreDataList")
    for node in node_list:
        data_list.append(node["value"])
    for data_file in data_list:
        getHdfsFile(hdfs_dir,data_file,local_data_dir+"/"+data_file)
    
# main
if __name__ == '__main__':
    if len(sys.argv) < 3:
        "Wrong usage: python HdfsUtil setting.xml save"
        sys.exit(0)
    conf_str = sys.argv[1]
    cmd = sys.argv[2]
    if cmd == "save":
        saveData(conf_str)
    elif cmd == "restore":
        restoreData(conf_str)
        
    conf = HexinConfiguration(conf_str)
    hdfs_dir = conf.getProperty("Configuration.hdfs_dir.value")
    print lsHdfsDir(hdfs_dir)
    '''mkHdfsDir(hdfs_dir)
    putHdfsFile(hdfs_dir,"neg_dict","data/neg_dict")
    putHdfsFile(hdfs_dir,"pos_dict","data/pos_dict")
    putHdfsFile(hdfs_dir,"stopwords.txt","data/stopwords.txt")
    putHdfsFile(hdfs_dir,"orig_word","data/orig_word")
    putHdfsFile(hdfs_dir,"myhexin.trade.kdd.txt","data/myhexin.trade.kdd.txt")
    '''
    
