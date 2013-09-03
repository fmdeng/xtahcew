#!/usr/bin/env python
# -*- coding:utf-8 -*-

import MySQLdb
import logging
import types
import traceback
import urlparse
import sys
import re
class MySqlHelper:
    
    def open(self, host_str, port_str, user_str, password_str, db_str):
        '''
        打开一个数据库连接
        '''
        try:
            conn = MySQLdb.connect(host=host_str, port=port_str, user=user_str, passwd=password_str, db = db_str, reconnect=1)
            self.write(conn,"set names utf8")

            logging.info("MYSQL DB CONNECTION OK ....")
            return conn
        except:
            logging.error("MySQL connection wrong !!!") 
            logging.error(str(host_str )+ " " + str(port_str) + "\t" + str(user_str) + "\t" + str(password_str) + "\t" + str(db_str))
            logging.error(traceback.format_exc())
            return None
    

    def readlines(self, conn, command, need_count =-1):
        '''
        给定一个command 和一个connection, 执行select 相关的command 将结果放到一个数组lines里面.
        每一个元素是一条记录，每个field用\t分隔开
        如果指定了need_count而且need_count大于0，最多放回need_count个结果
        如果执行出错，返回None
        '''
        conn.ping()
        lines = []
        try:
            cursor = conn.cursor ()
            cursor.execute(command)
            lines = []
            count = 0
            while ( need_count < 0 or (need_count > 0 and  count <  need_count) ):
                line = ""
                row = cursor.fetchone()
                if row == None:
                    break ;
                for item in row:
                    item = str(item).strip()
                    item = re.sub("\t", " ", str(item))
                    if cmp(line, "") <> 0:
                        line = line + "\t"  
                    line = line +  str(item)
                lines.append(line)
                count = count + 1 
            cursor.close()
            conn.commit()
        except:
            logging.error("MySQL read wrong! [%s]" %(command))
            logging.error(traceback.format_exc())
            return None
        return lines

    def setUTF8(self, conn):
        return self.write(conn,"set names utf8")
    def write(self, conn, command):
        try:
            conn.ping()
            cursor = conn.cursor ()
            cursor.execute("set names utf8")
            cursor.execute(command)
            cursor.close()
            conn.commit()
            return cursor.rowcount

        except:
            logging.error("Writting error [%s] !" %(command) )
            logging.error(traceback.format_exc())
            return -1
    
    def close(self, conn):
        conn.close()


if __name__ == "__main__":
    mysql  = MySqlHelper()
    handle = mysql.open("172.20.0.52", 3306 , "wc" ,"kernel", "web_stockpick")
    
    #handle = mysql.open("192.168.23.105", 3306 , "root" ,"kernel", "textclass")
    sql_str = "REPLACE INTO human_ontology(task_name,subject_uri,subject_label,predicate_uri,predicate_label,literal,source_text,source_uri) VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"
    sql = """SELECT c.`id`,c.`name`,count(*) FROM `concept_list` as c,search_admin.norwd_wordslist as w where c.`id`=w.typeid group by c.`id` order by c.id desc """
    sql = """SELECT * FROM `ner_entity` WHERE status = '1' AND type = 'PRO' AND task NOT LIKE 'ifind%'"""
    sql = ''' SELECT * FROM `rel_product_stock` where task like '%tao%' '''
    sql = """ select * from updatedict """
    data = mysql.readlines(handle, sql)
    print data
    for item in data:
        item = item.strip().split("\t")

        print item[2], item[3], item[4]
