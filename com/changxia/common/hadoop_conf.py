#!/usr/bin/python
#-*-coding:utf-8-*-
import os
'''
需要操作hdfs的时候，需要设置以下环境变量
e.g.:
import commands
sys.path.append("../../src/python")
from common.hadoop_conf import *
command = "hadoop dfs -ls /"
(status, output) = commands.getstatusoutput(command + "  2>/dev/null")
print status
print output

注意： 当前运行的机器上必须有一个hadoop用户，并且在其下面部署了标准的hadoop(可以咨询分布式项目组 liangyi@myhexin.com)
'''
os.environ['DFS_USER']='hadoop'
os.environ['DFS_HOME']='/home/%s'%os.environ['DFS_USER']
os.environ['DFS_ENV']='%s/dfs.env.sh'%os.environ['DFS_HOME']
os.environ['DFS_CONF_DIR']='%s/conf'%os.environ['DFS_HOME']
os.environ['JAVA_HOME']='%s/jdk1.6.0_23'%os.environ['DFS_HOME']
os.environ['HADOOP_HOME']='%s/hadoop'%os.environ['DFS_HOME']
os.environ['HADOOP_CONF_DIR']='%s/conf'%os.environ['HADOOP_HOME']
os.environ['HBASE_HOME']='%s/hbase'%os.environ['DFS_HOME']
os.environ['PATH']='%s:%s/bin'%( os.environ["PATH"] , os.environ['HADOOP_HOME'] )


