#!/usr/bin/python
#-*- coding: utf-8 -*-

from ctypes import *

lib_handle = CDLL("./dat.so.2")

#build bin
py_buildTree = lib_handle.buildTree
py_buildTree("synonym.txt","test.synonym.txt1.bin")

#load bin
py_loadBin = lib_handle.loadBin
py_loadBin.restype = c_void_p
dataStructre = py_loadBin("test.synonym.txt1.bin")

#search
py_search = lib_handle.search
tag = c_bool(0)
py_search.restype = c_char_p
result = py_search("阿拉丁在埃及和阿拉伯吗, 你想研究生物学吗", dataStructre, tag)
print result

#free python版本释放指针有问题
#py_freeResult = lib_handle.freeResult
#py_freeResult(result)

#delete
py_destroyBin = lib_handle.destroyBin
py_destroyBin(dataStructre)
