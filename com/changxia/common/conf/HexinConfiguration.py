#!/usr/bin/python
#-*-coding:utf-8-*-
import xml.dom.minidom
import sys
import os
import logging
import traceback
'''
从xml读取配置的模块
'''
class HexinConfiguration(object):
    NODE_NAME="<nodename>"

    def __init__(self, parameter):
        self.configuration_dict = {}
        self.configuration_dict_node_list = {}
        self.dom = None
        self.init_ok = False
        if os.path.exists(parameter):
            try:
                self.dom = xml.dom.minidom.parse(parameter)
            except:
                self.dom = None
                logging.error("init xml file %s[[\n%s\n]]"%(parameter, traceback.format_exc()))
        else:
            try:
                self.dom = xml.dom.minidom.parseString(parameter)
            except:
                self.dom = None
                logging.error("init xml string %s[[\n%s\n]]"%(parameter, traceback.format_exc()))

        #parse all the xml info
        if self.dom == None:
            return
        self.init_ok = self.extractDictsFromDom(self.dom.documentElement, "")

    def extractDictsFromDom(self, xml_node, parent):
        if xml_node == None:
            return
        my_name = xml_node.tagName
        node_list_info = []
        for (key,value) in xml_node.attributes.items():
            #add property
            self.configuration_dict[str(parent +my_name +"." + key)] = value.encode("utf-8")
        for node in xml_node.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                self.extractDictsFromDom(node, parent + my_name + ".")
                #prepare the node list
                tmp_dict = {}
                tmp_dict[str(HexinConfiguration.NODE_NAME)] = str(node.tagName)
                for (key,value) in node.attributes.items():
                    tmp_dict[str(key)] = value.encode("utf-8")
                node_list_info.append(tmp_dict)
        self.configuration_dict_node_list[str(parent +my_name)] = node_list_info
        return True


    def getProperty(self, path_str, default="None"):
        '''
        获得某一个属性值，如获得Jobserver的名字
        getProperty(root.jobserver.name)
        没有配置返回default
        '''
        if path_str in self.configuration_dict:
            return self.configuration_dict[path_str]
        return default

    def getNodeList(self, path_str, default = []):
        '''
        获得一个nodelist，如获得jobserver的ip，port
        getNodeList(root.jobserver.locations)
        返回[ {"<nodename>":"location", "ip":xxx, "port":xxx}, {"<nodename>":"location", "ip":xxx, "port":xxx}]
        '''
        if path_str in self.configuration_dict_node_list:
            return self.configuration_dict_node_list[path_str]
        else:
            return default

    '''
    '''
    def setPropertiy(self, path_str, value="None"):
        self.configuration_dict[str(path_str)] = str(value)
        pass

    '''
    '''
    def setNodeList(self, path_str, value = []):
        self.configuration_dict_node_list[path_str] = value
        pass

    def dumpConfig(self):
        result = "----------------config---------------\n"
        result += "----------------ATTR---------------\n"
        for item in self.configuration_dict:
            result +="%s\t%s\n"%(item, self.configuration_dict[item])
        result += "----------------Node---------------\n"
        for item in self.configuration_dict_node_list:
            result +="%s\t%s\n"%(item, self.configuration_dict_node_list[item])
        result += "----------------config---------------\n"
        return result

if __name__ == "__main__":
    xmlstr = """<?xml version="1.0" encoding="UTF-8"?>
<Configuration app="fortest">
	<ruleTxt value="../data/SimpleRecognition/tools/recognition/data/rules.txt"/>
	<featureTxt value="../data/SimpleRecognition/tools/recognition/data/myhexin.trade.kdd.txt"/>
    <featureBin value="../data/SimpleRecognition/tools/recognition/data/myhexin.trade.kdd.txt.bin"/>
    <featureOtherBin value="../data/SimpleRecognition/tools/recognition/data/myhexin.trade.kdd.txt.other.bin"/>
    <db>
        <!--只做exactly match-->
        <instance name="posneg" one="../data/SimpleRecognition/tools/recognition/data/relation.txt.bin"/>
    </db>

    <pinglun>
        <recog value="10010"/>
        <class value="132"/>
        xxx
    </pinglun>
    <shouyigu>
        <recog value="测试"/>
        <class value="133"/>
    </shouyigu>
    <importantnews>
        <recog value="1000"/>
        <class value="20000"/>
    </importantnews>
</Configuration>
    """
    conf = HexinConfiguration(xmlstr)
    print conf.getProperty("Configuration.shouyigu.recog.value")
    print conf.getNodeList("Configuration")
    #print conf.dumpConfig()
