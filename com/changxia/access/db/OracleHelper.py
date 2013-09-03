# -*- coding:utf-8 -*-
'''
#执行前请设置以下环境变量:
    #export ORACLE_HOME="/opt/oracle/instantclient_11_2"
    #export PATH=$PATH:$ORACLE_HOME/bin
    #export LD_LIBRARY_PATH=$ORACLE_HOME:$ORACLE_HOME/lib:/lib:/usr/lib:/usr/local/lib
    #export TNS_ADMIN=$ORACLE_HOME/network/admin
#更多使用方法: http://www.oracle.com/technetwork/articles/dsl/python-091105.html
测试该程序直接运行 run.test.oracle.sh
'''
import os
os.environ['ORACLE_HOME'] = "/opt/oracle/instantclient_11_2"
import cx_Oracle
import logging
import traceback
import os

class OracleHelper:
    
    def connectODB(self):
        ''' 连接到104上的iFind数据库镜像  '''
        return self.connect("db40", "db40", "ODB")
    
    def connectIfind(self):
        '''连接到iFind数据库'''
        return self.connect("guest", "guest_110", "117")
            
    def connect(self, user_name, password, tns_name):
        '''连接到$ORACLE_HOME/network/admin/tnsnames.ora中指定的某个库'''
        try:
            os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8' 
            conn = cx_Oracle.connect(user_name + "/" + password + "@" + tns_name)
            logging.info(tns_name +" connected")
            return conn
        except:
            logging.error("failed to connect " + tns_name)
            traceback.print_exc()
    
    def close(self, conn):
        conn.close()
    
if __name__ == "__main__":
    #connect DB
    oracle_helper = OracleHelper()
    oracle_conn = oracle_helper.connectIfind()
    cursor = oracle_conn.cursor()
    sql_usa = '''
        select seccode_pub205 "证券代码",
               SECNAME_PUB205 "证券简称（中文）",
                      F026V_PUB205 "证券简称（英文）",
                             decode(f005v_pub205, '212010', 'NYSE', '212011', 'NASDAQ', '212049', 'AMEX') as "交易市场简称",
                                    pub201.f001v_pub201 "交易市场"
                                    from pub205
                                    left join pub201
                                    on F005V_PUB205 = pub201.code_pub201
                                    and F002V_PUB201 = '212'
                                    and pub201.isvalid = 1
                                    where pub205.isvalid = 1
                                    and f005v_pub205 in ('212010', '212011', '212049')
                                    order by 1


    '''
    sql_sanban = """
    select seccode_pub205        "证券代码",
           F016V_PUB205          "证券全称",
                  pub203.orgname_pub203 "发行机构名称"
                  from pub205
                  left join pub203
                  on F014V_PUB205 = pub203.orgid_pub203
                  and pub203.isvalid = 1
                  where pub205.isvalid = 1
                  and f002v_pub205 in ('001004')
                  order by 1

    """
    #cursor.execute("SELECT stockcode,STOCKSNAME from stk001")
    #cursor.execute(sql_sanban) ;
    #for row in cursor:
    #     print "%s\t%s\t%s"%(row[0], row[1], row[2])
    
    cursor.execute(sql_usa)
    for row in cursor:
         print ("%s\t%s\t%s\t%s\t%s"%(row[0], row[1], row[2], row[3], row[4]))

    cursor.close()
    oracle_conn.close()

