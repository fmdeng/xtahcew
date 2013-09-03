#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""httpsqs python 客户端"""

import urllib2
from urllib2 import URLError, HTTPError
import urllib
import sys

class httpsqsException(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg

class httpsqs:
    """为开源的message queue提供访问和设置的接口
    
    变量：
    host -- 指定httpsqs服务器IP地址
    port -- 指定httpsqs服务器端口
    charset -- 指定HTTP输出Header头的字符编码
    name -- 指定httpsqs中消息队列名

    函数：
    get() -- 获取并返回指定队列中一个元素
    put() -- 向队尾增加指定队列中一个元素
    status() -- 返回指定队列状态：元素个数上限，当前队头位置，当前队尾位置，未读元素个数
    status_json() -- 以JSON方式 返回指定队列状态，方便程序处理
    view() -- 查看指定队列位置点的内容

    reset() -- 重置指定队列，队列中所有的未读元素将丢失
    maxqueue() -- 更改指定队列中元素个数上限， 10 - 1,000,000,000 (默认1,000,000)
    synctime() -- 不停止服务的情况下，修改定时刷新内存缓冲区内容到磁盘的间隔时间
    """
    host = "127.0.0.1"
    port = '1218'
    charset = 'utf-8'
    name = ''
    
    def __init__(self, host, port, name, charset='utf-8'):
        """初始化参数,地址，端口，队列名称，字符编码
        
        参数：
        host -- 指定httpsqs服务器IP地址
        port -- 指定httpsqs服务器端口
        name -- 指定httpsqs中消息队列名
        charset -- 指定HTTP输出Header头的字符编码
        """
        self.host = host
        self.port = port
        self.name = name
        self.charset = charset
    
    def request(self, opt, data=None, name=None, method='GET', charset=None):
        """向指定的httpsqs服务器发送一个HTTP请求，执行消息队列操作

        参数：
        opt -- httpsqs支持的操作
        data -- 文本消息
        name -- 该请求操作的消息队列
        method -- 该请求使用的HTTP方法，默认为GET
        charset -- 指定HTTP输出Header头的字符编码

        返回值
        若发送成功，返回页面元数据和页面内容
        若发送失败，返回None
        """
        if name is None:
            name = self.name
        if charset is None:
            charset = self.charset
        param = {'charset':charset, 'name':name, 'opt':opt}
        
        url = 'http://' + self.host + ':' + self.port + '/?'

        if method == 'GET':
            if data :
                param.update(data)
            param_str = urllib.urlencode(param)
            url = url + param_str
            req = urllib2.Request(url)

        if method == 'POST':
            param_str = urllib.urlencode(param)
            url = url + param_str
            req = urllib2.Request(url, data)

        meta = None
        content = None
        try:
            handle = urllib2.urlopen(req)
        except HTTPError, e:
            raise httpsqsException('The server couldn\' t fulfill the request: %s' % e.code)
        except URLError, e:
            raise httpsqsException('URL error: %s' % e.reason)
        except:
            raise httpsqsException('Unknown error')
        else:
            meta = handle.info()
            content = handle.read()
        return (meta, content)
        
    def get(self, q_name=None):
        """获取指定队列队首元素

        参数：
        q_name -- 指定操作的队列名称

        返回值：
        若获取成功，返回队首元素消息内容
        否则，返回空字符串
        """
        (meta, content) = self.request('get', name=q_name)
        currentQ = (self.name if (q_name is None) else q_name)
        if content == 'HTTPSQS_ERROR':
            raise httpsqsException("Global error!")
        elif content == 'HTTPSQS_GET_END':
            raise httpsqsException("There is no data in queue: [" + currentQ + "]")
        
        return content
        
    def put(self, data, q_name=None):
        """向指定队列队尾增加一个元素

        参数：
        data -- 文本消息
        q_name -- 指定操作的队列名称

        返回值：
        无

        若操作失败，抛出异常
        """
        (meta, content) = self.request('put', {'data':data}, q_name)
        currentQ = (self.name if (q_name is None) else q_name)

        if content == 'HTTPSQS_ERROR':
            raise httpsqsException("Global error!")
        elif content == 'HTTPSQS_PUT_END':
            raise httpsqsException("Queue [" + currentQ + "] fulled.")
        elif content == 'HTTPSQS_PUT_ERROR':
            raise httpsqsException("Put data to queue [" + currentQ + "] failed.")
        
    def reset(self, q_name=None):
        """重置指定消息队列

        参数：
        q_name -- 指定操作的队列名称

        返回值：
        若操作成功，返回True
        若操作失败，返回False
        """
        (meta, content) = self.request('reset', name=q_name)
        if content == 'HTTPSQS_ERROR':
            raise httpsqsException("Global error!")
        elif content == 'HTTPSQS_RESET_OK':
            return True
        else:
            return False
    
    def maxqueue(self, num, q_name=None):
        """更改指定队列的元素个数上限

        参数：
        num -- 队列的元素个数上限 (10 - 1,000,000,000)
        q_name -- 指定操作的队列名称

        返回值：
        若操作成功，返回True
        若操作失败，返回False
        """
        if not num:
            return False
        
        (meta, content) = self.request('maxqueue', {'num':num}, q_name)
        if content == 'HTTPSQS_ERROR':
            raise httpsqsException("Global error!")
        elif content == 'HTTPSQS_MAXQUEUE_OK':
            return True
        else:
            return False
        
    def status_json(self, q_name=None):
        """以json格式返回指定队列状态等信息

        参数：
        q_name -- 指定操作的队列名称

        返回值：
        若操作成功，返回json格式的文本
        否则，返回空字符串
        """
        (meta, content) = self.request('status_json',  name=q_name)
        if content == 'HTTPSQS_ERROR':
            raise httpsqsException("Global error!")
        return content
        
    def synctime(self, num, q_name=None):
        """不停止服务的情况下，修改定时刷新内存缓冲区内容到磁盘的间隔时间

        参数：
        num -- 间隔时间
        q_name -- 指定操作的队列名称

        返回值：
        若操作成功，返回True
        若操作失败，返回False
        """
        if not num:
            return False

        (meta, content) = self.request('synctime', {'num':num}, q_name)
        if content == 'HTTPSQS_ERROR':
            raise httpsqsException("Global error!")
        elif content == 'HTTPSQS_SYNCTIME_OK':
            return True
        else:
            return False
    
    def status(self, q_name=None):
        """获取指定队列状态信息

        参数：
        q_name -- 指定操作的队列名称

        返回值：
        若操作成功，返回指定队列的状态信息
        否则，返回空字符串
        """
        (meta, content) = self.request('status', name=q_name)
        if content == 'HTTPSQS_ERROR':
            raise httpsqsException("Global error!")
        return content
        
    def view(self, pos, q_name=None):
        """查看指定队列位置点的内容

        参数：
        pos -- 队列位置
        q_name -- 指定操作的队列名称

        返回值：
        若操作成功，返回指定队列位置点的内容
        否则，返回空字符串
        """
        (meta, content) = self.request('view', {'pos':pos}, q_name)
        if content == 'HTTPSQS_ERROR':
            raise httpsqsException("Global error!")
        
        return content
