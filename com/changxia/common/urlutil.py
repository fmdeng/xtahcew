#!/usr/bin/python
#-*-coding:utf-8-*-
"""
This module contains general purpose URL functions not found in the standard
library.
"""

import os
import re
import urlparse
import urllib
import types
import hashlib
import sys
import logging
import urlparse
def get_uid(url):
    """
        get the uid of the url
        algorithm:
        1) get 16 bytes (128 bits) md5, encoded by hex
        2) split the first 8 bytes and the last 8 bytes
        3) convert the two 8 bytes into int
        4) XOR the two 8 bytes
        5) encode the result by hex
    """
    if isinstance(url, types.StringType):
        # md5 is a string represents a 32bytes hex number
        md5 = hashlib.new("md5", url).hexdigest()
        first_half_bytes = md5[:16]
        last_half_bytes = md5[16:]
        
        # get the two long int
        first_half_int = int(first_half_bytes, 16)
        last_half_int = int(last_half_bytes, 16)
        
        # XOR the two long int, get a long int
        xor_int = first_half_int ^ last_half_int
        
        # convert to a hex string
        uid = "%x" % xor_int
        
        return uid
    return "AA"


if __name__ == "__main__":
    """urls = ['http://finance.sina.com.cn/g/20110330/06229614174.shtml',
            'http://finance.sina.com.cn/review/hgds/20110330/08459615190.shtml',
            'http://finance.qq.com/a/20110330/000945.htm']"""

    urls = ['http://www.10jqka.com.cn']
    urls.append(sys.argv[1])
    for url in urls:
        uid = get_uid(url)
        print "url =%s\t\tuid=%s" % (url, uid )

