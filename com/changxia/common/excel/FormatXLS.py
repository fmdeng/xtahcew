#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
'''
将一个<tab>隔开的文件格式化为excel
执行之前需要安装
https://pypi.python.org/packages/source/x/xlwt/xlwt-0.7.5.tar.gz
'''
from xlwt import *
if __name__ == "__main__":
    if len(sys.argv) <> 3:
        print "usage: %s: <input_file> <output_file>\n"
        sys.exit(1)
    lines = open(sys.argv[1], "r").readlines()
    file_out = sys.argv[2]
    style0 = XFStyle()
    wb = Workbook(encoding='utf8')
    ws0 = wb.add_sheet('0', cell_overwrite_ok=True)
    row_index = 0
    for item in lines:
        item = item.strip().split("\t")
        column_index = 0
        colum_range = len(item)
        for column_index in xrange(colum_range):
            content = item[column_index]
            print content
            ws0.write(row_index, column_index, item[column_index], style0)
        row_index += 1
    wb.save(file_out)
