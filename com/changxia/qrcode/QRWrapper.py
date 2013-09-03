#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
生成二维码
扫描二维码
'''
import os
import qrcode
import sys
sys.path.append("../../../")
import traceback
from com.changxia.common.urlutil import *

class QRWrapper(object):

    def __init__(self, dir_name):
        self.initOK = False
        try:
            self.init(dir_name)
            self.initOK = True
        except:
            logging.error("QRWrapper init wrong " + traceback.format_exc())
    
    def init(self, dir_name):
        self.dir_name = dir_name
        if not os.path.exists(self.dir_name):
            os.popen("mkdir -p " + self.dir_name).read()
        elif os.path.isfile(self.dir_name):
            raise Exception("File exists for QR file " + self.dir_name) 
        else:
            pass
    def generateQRCode(self, content, filename = None):
        '''
        生成二维码，成功：返回二维码的文件， 否则返回None
        '''

        if self.initOK == True:
            try:
                if filename == None:
                    filename = get_uid(content ) + ".jpeg"
                img = qrcode.make(content)
                abs_filename = self.dir_name + "/" + filename
                img.save(abs_filename)
                return abs_filename
            except:
                logging.error("Generate QRCode wrong " + traceback.format_exc()) 
                return None
        else:
            return None


if __name__ == "__main__":
   qr_code_wrapper = QRWrapper("./")
   qr_code_wrapper.generateQRCode(sys.argv[1], sys.argv[2])
   qr_code_wrapper.generateQRCode(sys.argv[3] )
