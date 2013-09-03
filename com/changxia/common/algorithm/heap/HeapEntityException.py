#!/usr/bin/python
class HeapEntityException(Exception):
    def __init__(self,msg):
        Exception.__init__(self)
        self.message = msg
    def __str__(self):
        return self.message

