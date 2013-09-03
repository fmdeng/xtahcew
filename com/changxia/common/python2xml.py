#!/usr/bin/env python
#-*-coding:utf-8-*-
import logging,types,traceback
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
def isBuiltinType(obj):
    built_types = [types.NoneType,types.BooleanType,types.IntType,types.LongType,types.FloatType,types.ComplexType,types.StringType,types.UnicodeType]
    for built_type in built_types:
        if isinstance(obj,built_type):
            return True
    return False
        
class Converter(object):
    root = None#根节点
    def __init__(self):
        pass
    @staticmethod
    def createRoot(curTag,parNode=None):
        if parNode == None:
            cur = ET.Element(curTag)
        else:
            cur = ET.SubElement(parNode,curTag)
        return cur
    @staticmethod
    def getXmlString(element,defaultEncoding='utf-8'):
        try:
            rough_string = ET.tostring(element, defaultEncoding)
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  " , encoding=defaultEncoding)
        except:
            print 'getXmlString:传入的节点不能正确转换为xml，请检查传入的节点是否正确'
            return ''
    @staticmethod
    def ElementToXML(attrvalue,parNode=None):
        #logging.debug('parse ElementToXML:'+str(attrvalue))
        if isinstance(attrvalue, types.ListType) or isinstance(attrvalue, types.TupleType) or isinstance(attrvalue,types.DictType):
            attrE = Converter.collectionToXML(attrvalue,parNode)
        elif (not isBuiltinType(attrvalue)):
            attrE = Converter.classToXML(attrvalue,parNode)
        elif isinstance(attrvalue,types.UnicodeType):
            attr = attrvalue.__class__.__name__ #类名
            attrE = Converter.createRoot(attr,parNode)
            attrE.text = attrvalue.encode("utf-8")
        else:
            attr = attrvalue.__class__.__name__ #类名
            attrE = Converter.createRoot(attr,parNode)
            attrE.text = str(attrvalue)
        return attrE
    @staticmethod
    def classToXML(classobj,parNode=None):
        #logging.debug('parse classToXML:'+str(classobj))
        attrs = None#保存对象的属性集
        cur = None
        try:
            classname = classobj.__class__.__name__ #类名
            cur = Converter.createRoot(classname,parNode)
            attrs = classobj.__dict__.keys()#获取该对象的所有属性(即成员变量)
        except:
            print 'classToElements:传入的对象非法，不能正确获取对象的属性'+str(classobj)
        if attrs != None and len(attrs) > 0:#属性存在
            for attr in attrs:
                attrvalue = classobj.__dict__[attr]
                itemE = Converter.ElementToXML(attrvalue,cur)
                itemE.set('name', attr)
        return cur
    @staticmethod
    def collectionToXML(listobj,parNode=None,curTag='list'):
        #logging.debug('parse collectionToXML:'+str(listobj))
        try:
            classname = listobj.__class__.__name__ #类名
            #if curTag == 'list':
            cur = Converter.createRoot(classname,parNode)
            #else:
            #    cur = Converter.createRoot(curTag,parNode)
            if isinstance(listobj, list) or isinstance(listobj, tuple):#列表或元组
                if len(listobj) >= 0:
                    for obj in listobj:#迭代列表中的对象
                        itemE = Converter.ElementToXML(obj,cur)
            elif isinstance(listobj, dict):#字典
                if len(listobj) >= 0:
                    for key in listobj:#迭代字典中的对象
                        obj = listobj[key]
                        itemE = Converter.ElementToXML(obj,cur)
                        itemE.set('key', key)
            else:
                print 'listToXML：转换错误，传入的对象：'+classname+'不是集合类型'
            return cur
        except:
            print traceback.print_exc()
            print 'collectionToXML：转换错误，集合转换成xml失败'+classname
            return None
if __name__ == '__main__':
    #root = Converter.collectionToXML(personList)
    print "的烦恼"
