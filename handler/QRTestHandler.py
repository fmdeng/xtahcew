#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os.path
import sys
sys.path.append("../")
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from com.changxia.qrcode.QRWrapper import *
from setting import *
'''
测试二维码
'''
class QRTestHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.qrwrapper = QRWrapper(QRCODE_DIR)
        input_content = self.get_argument('content')
        if input_content == None:
            input_content = "http://www.iwencai.com/"
        logging.info("get content " + input_content)
        qrcode_img =  self.qrwrapper.generateQRCode(input_content)
        self.render(
            "qrtest/index.html",
            content = input_content,
            qrcodeimg = qrcode_img,
        )

if __name__ == "__main__":
    qrwrapper = QRWrapper(QRCODE_DIR)

    input_content = "http://www.iwencai.com/"
    qrcode_img =  qrwrapper.generateQRCode(input_content)
    
