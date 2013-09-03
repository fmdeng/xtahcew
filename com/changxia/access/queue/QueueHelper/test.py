#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pyhttpsqs import httpsqs
from pyhttpsqs import httpsqsException
if __name__=="__main__":
    sqs = httpsqs(host="192.168.23.207", port='1218', name="caijingwenju_dev")
    try:
        content = sqs.status()
        print content
        #raise  httpsqsException("fuck here")
        raise 2
    except httpsqsException as e:
        print e.message
    except:
        print "here"

