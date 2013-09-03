#!/usr/bin/python
#-*-coding:utf-8-*-
import sys
import os
import re,logging
import curses.ascii
sys.path.append("../")
from access.ltp.LtpHelper import *
from common.DictionarySearcher import *
from common.strutil import *
from setting import *
# search option
# support for same word with different tag type by involve position info
TAG_MAP_DIVIDER="__"
UNI_TAG_POS="0"
'''feature type supported
   char --- chinese char feature, only one char,
   word --- chinese char feature, maybe multi char,
   segment --- word segment tag produced by ltp
   pos --- word segment&pos tag produced by ltp
   dict --- entity tag, matched by entity dictionary
   pattern --- entity tag, matched by regular grammar pattern
   crf --- entity tag, produced by crf

   common feature list:
   1) char|pos|dict
   2) char|dict
   3) char|segment|dict
'''
FEATURE_CHAR="char"
FEATURE_WORD="word"
FEATURE_SEGMENT="segment"
FEATURE_POS="pos"
FEATURE_DICT="dict"
FEATURE_PATTERN="pattern"
FEATURE_HUMAN="human"
''' conf name '''
CONF_FEATURE_STRING="feature_string"
CONF_FEATURE_REPTYPE="feature_reptype"
CONF_DICT_FILE="dict_file"
CONF_PATTERN_FILE="pattern_file"
CONF_FILTERWORD_FILE="filterword_file"
INVALID_FILE="###"
LTP_ENV="TEST"
class GenerateTag:

    def __init__(self,conf_map=None):
        # default conf
        if conf_map == None:
            conf_map = {}
            conf_map[CONF_FEATURE_STRING] = "char|dict"
            conf_map[CONF_FEATURE_REPTYPE] = "BIO"
            conf_map[CONF_DICT_FILE] = INVALID_FILE
            conf_map[CONF_PATTERN_FILE] = INVALID_FILE
            conf_map[CONF_FILTERWORD_FILE] = INVALID_FILE
        # ltp option
        self.ltp_ip=LTPSERVER[LTP_ENV]["Host"]
        self.ltp_port=int(LTPSERVER[LTP_ENV]["Port"])
        self.ltpClient = LtpHelper(self.ltp_ip,self.ltp_port,None)
        # tag option
        self.BEGIN_TAG="B"
        self.INTER_TAG="I"
        self.END_TAG="E"
        self.SINGLE_TAG="S"
        self.OTHER_TAG="O"
        self.TAG_DIV="-"
        self.has_end_tag=False
        self.has_single_tag=False
        # feature option
        self.FEA_DIV="|"
        self.FEA_SUBDIV="_"
        # filter word option
        self.common_tag="COMMON"
        # prepare data info
        self.initTagger(conf_map)
    
    def __del__(self):
        pass
    '''#############getter and setter#################'''
    def getFeatureDict(self, feature_type):
        if feature_type in self.data_map:
            return self.data_map[feature_type]
        else:
            return None
    def getEntityMap(self):
        return self.entity_map

    def setFeatureDict(self, feature_type, tag_dict):
        self.data_map[feature_type] = tag_dict
    '''#############main process#################'''
    # reset tager 
    def resetTagger(self):
        logging.info("start resetTagger()")
        self.data_map = {}
        self.charword_map = {}
        self.content = ""
    
    # generate features
    def mkTag(self,content,external_segment=None):
        logging.info("start mkTag()")
        # run ltp first 
        segment_list = []
        if self.segment_based:
            if external_segment == None:
                segment_list = self.getLtpResult(self.ltpClient,content)
            else:
                segment_list = external_segment
            tmp_string = ""
            for word_item in segment_list:
                (word, pos_tag) = word_item
                tmp_string += word
            # ltp may remove some char
            content = tmp_string
        self.content = content
        # generate feature
        for tmp_list in self.feature_list:
            for item in tmp_list:
                if item in self.data_map:
                    logging.error("error: add same feature twice!!")
                    continue
                if item == FEATURE_CHAR:
                    self.data_map[item] = self.generateCharFeature(content)
                elif item == FEATURE_WORD:
                    (tag_dict, charword_map) = self.generateWordFeature(segment_list)
                    self.data_map[item] = tag_dict
                    self.charword_map = charword_map
                elif item == FEATURE_SEGMENT:
                    self.data_map[item] = self.generateSegmentFeature(segment_list)
                elif item == FEATURE_POS:
                    self.data_map[item] = self.generatePosFeature(segment_list)
                elif item == FEATURE_DICT:
                    self.data_map[item] = self.generateDictFeature(content, self.dict_search, self.search_tagmap)
                elif item == FEATURE_PATTERN:
                    self.data_map[item] = self.generatePatternFeature(content)
    # generate char feature
    @staticmethod
    def generateCharFeature(content):
        logging.info("start generateCharFeature()")
        content_uni = content.decode("utf-8")
        cnt = 0
        ret_map = {}
        while cnt < len(content_uni):
            ret_map[str(cnt)] = content_uni[cnt].encode("utf-8")
            cnt += 1
        return ret_map
    # cal position for each word 
    @staticmethod
    def generateWordFeature(self, segment_list):
        logging.info("start generateWordFeature()")
        cnt = 0
        ret_map = {}
        total_pos = 0
        charword_map = {}
        for (word,tag) in segment_list:
            word_len = len(word.decode("utf-8"))
            ret_map[str(cnt)] = word
            charword_map[str(total_pos)] = (cnt,word_len)
            total_pos += word_len
            cnt += 1
        return (ret_map,charword_map)
    # cal position for each word 
    def generateSegmentFeature(self, segment_list):
        logging.info("start generateSegmentFeature()")
        tag_dict = {}
        total_pos = 0
        for (word,tag) in segment_list:
            word_uni = word.decode("utf-8")
            word_len = len(word_uni)
            self.markTag(tag_dict,total_pos,word_len)
            total_pos += word_len
        return tag_dict
    # cal position for each word 
    def generatePosFeature(self, segment_list):
        logging.info("start generatePosFeature()")
        tag_dict = {}
        total_pos = 0
        for (word,tag) in segment_list:
            word_uni = word.decode("utf-8")
            word_len = len(word_uni)
            self.markTag(tag_dict,total_pos,word_len,tag)
            total_pos += word_len
        return tag_dict
    # Get tag by search with word list
    def generateDictFeature(self, string, searcher, tagmap, all_search=False):
        logging.info("start generateDictFeature()")
        # preform max search first
        tag_dict = {}
        # all search
        if all_search:
            (matched_item, len_txt) = searcher.searchAll(string, "utf-8", True, False)
        else:
            (matched_item, len_txt) = searcher.maxSearchEx(string, "utf-8")
        for item in matched_item:
            word_len = len(item)
            word = item.encode("utf-8")
            pos = 1
            for start in matched_item[item]:
                # mark tag, different position different tag
                uni_tag_code = word+TAG_MAP_DIVIDER+UNI_TAG_POS
                pos_tag_code = word+TAG_MAP_DIVIDER+str(pos)
                if pos_tag_code in tagmap:
                    self.markTag(tag_dict,int(start),word_len,tagmap[pos_tag_code])
                elif uni_tag_code in tagmap:
                    self.markTag(tag_dict,int(start),word_len,tagmap[uni_tag_code])
                pos += 1
        return tag_dict
    # Get tag by search with pattern list
    def generatePatternFeature(self, string):
        logging.info("start generatePatternFeature()")
        tag_dict = {}
        # try every pattern
        for (pattern_des,tag) in self.pattern_list:
            try:
                pattern = re.compile(pattern_des,flags=re.IGNORECASE)
            except re.error:
                continue
            for m in pattern.finditer(string):
                (m_start,m_end) = m.span()
                # find out wrong word
                if self.filterByWord(string[m_start:m_end],tag):
                    continue
                # print out pattern
                if m_start == 0:
                    uni_start = 0
                else:
                    uni_start = len(string[0:m_start].decode("utf-8"))
                uni_end = len(string[0:m_end].decode("utf-8"))
                #logging.debug("%s\t%s"%(string[m_start:m_end],pattern_des))
                self.markTag(tag_dict,uni_start,uni_end-uni_start,tag)
        return tag_dict

    '''#############format transformer function#################'''
    # transform position dict to string
    def transDictToTagstring(self, content, tag_dict):
        # get labeled word list
        chunk_list = self.getChunkFromTag(content, tag_dict)
        all_search = DictionarySearcher()
        for (chunk, flag,tag) in chunk_list:
            if flag:
                all_search.addKey(chunk)
        # Check each occurs
        bFirst1 = True
        total_str = ""
        (matched_item, len_txt) = all_search.searchAll(content, "utf-8", True, False)
        for item in matched_item:
            word_len = len(item)
            word = item.encode("utf-8")
            tmp_str = "%s:"%(word)
            word_cnt = 1
            bFirst2 = True
            for m_start in matched_item[item]:
                if self.isValidChunk(tag_dict, int(m_start), word_len):
                    tmp_list =tag_dict[str(m_start)].split("-")
                    if len(tmp_list) == 2:
                        tag = tmp_list[1]
                    else:
                        tag = ""
                    if bFirst2:
                        bFirst2 = False
                        tmp_str += str(word_cnt)+"_"+tag
                    else:
                        tmp_str += (","+str(word_cnt)+"_"+tag)
                word_cnt += 1
            if bFirst1:
                total_str += tmp_str
                bFirst1 = False
            else:
                total_str += (" " + tmp_str)
        return total_str
    # transform tagstring to dict
    def transTagstringToDict(self,content,tag_string):
        tag_map = {}
        all_search = DictionarySearcher()
        tmp_list2 = tag_string.split(" ")
        for item2 in tmp_list2:
            tmp_list3 = item2.split(":")
            word = tmp_list3[0]
            tmp_list4 = tmp_list3[1].split(",")
            for item4 in tmp_list4:
                tmp_list5 = item4.split("_")
                pos = tmp_list5[0]
                tag = tmp_list5[1]
                tag_map[word+TAG_MAP_DIVIDER+pos] = tag
                all_search.addKey(word)
        return self.generateDictFeature(content, all_search, tag_map, True)
    # word based transform if need
    def wordBasedTransform(self):
        logging.info("start wordBasedTransform()")
        if not self.word_based:
            return False
        for key in self.data_map:
            if key == FEATURE_CHAR or key == FEATURE_WORD:
                continue
            old_dict = self.data_map[key]
            new_dict = {}
            chunk_list = self.getChunkFromTag(self.content,old_dict)
            chunk_pos = 0
            for (chunk, flag,tag) in chunk_list:
                word_len = len(chunk.decode("utf-8"))
                if not flag:
                    chunk_pos += word_len
                    continue
                adj_index = self.charIndexToWordIndex(chunk_pos,word_len)
                if adj_index == None:
                    chunk_pos += word_len
                    continue
                (adj_start,adj_len) = adj_index
                if key == FEATURE_POS:
                    new_dict[str(adj_start)] = tag
                else:
                    self.markTag(new_dict,adj_start,adj_len,tag)
                chunk_pos += word_len
            self.data_map[key] = new_dict
        return True
            
    # output tag info
    def outputByCrfFormat(self):
        logging.info("start outputByCrfFormat()")
        # merge feature tags in same column
        merged_tag = []
        for tmp_list in self.feature_list:
            # no need do merge
            if len(tmp_list) == 1:
                merged_tag.append(self.data_map[tmp_list[0]])
                continue
            # merge
            tmp_tag = {}
            for item in tmp_list:
                # error check
                if not item in self.data_map:
                    print "no result for tag_type : %s"%item
                    return ""
                tmp_tag = self.mergeTagDictEx(self.content, tmp_tag, self.data_map[item])
            merged_tag.append(tmp_tag)
        # cal line num
        line_num = len(self.content.decode("utf-8"))
        if FEATURE_CHAR in self.data_map:
            line_num = len(self.data_map[FEATURE_CHAR])
        elif FEATURE_WORD in self.data_map:
            line_num = len(self.data_map[FEATURE_WORD])
        # output feature
        inx = 0
        ret_value = ""
        while inx < line_num:
            inx_str = str(inx)
            column_inx = 1
            for tmp_map in merged_tag:
                if inx_str in tmp_map:
                    tag = tmp_map[inx_str] 
                else:
                    tag = self.OTHER_TAG
                if column_inx == 1:
                    ret_value +="%s"%(tag)
                else:
                    ret_value +="\t%s"%(tag)
                column_inx += 1
            ret_value +="\n"
            inx +=1
        ret_value +="\n"
        return ret_value
    '''#############init function#################'''
    # init tagger
    def initTagger(self,conf_map):
        self.initEntityInfo(conf_map[CONF_DICT_FILE])
        self.initPatternInfo(conf_map[CONF_PATTERN_FILE],conf_map[CONF_FILTERWORD_FILE])
        self.initFeatureInfo(conf_map[CONF_FEATURE_STRING])
        self.initRepTypeInfo(conf_map[CONF_FEATURE_REPTYPE])
    
    # load entity info
    def initEntityInfo(self, file_name):
        self.search_tagmap = {}
        self.entity_map = {}
        self.dict_search = DictionarySearcher()
        if file_name == INVALID_FILE:
            return
        # read entity list
        self.entity_map = self.ReadKeyValue(file_name)
        for word in self.entity_map:
            tag = self.entity_map[word]
            self.dict_search.addKey(word);
            self.search_tagmap[word+TAG_MAP_DIVIDER+UNI_TAG_POS] = tag

    # load entity info
    def initPatternInfo(self, pattern_file,filter_file):
        # prepare pattern list
        self.pattern_list = []
        if pattern_file != INVALID_FILE:
            self.pattern_list = self.ReadPairWord(pattern_file)
        # prepare filter search
        self.filter_search = {}
        filter_item = {}
        if filter_file != INVALID_FILE:
            filter_item = self.ReadKeyValue(filter_file)
        # create searcher first
        for word in filter_item:
            tag = filter_item[word]
            if tag != self.common_tag and (not tag in self.filter_search):
                self.filter_search[tag] = DictionarySearcher()
        # add words
        for word in filter_item:
            tag = filter_item[word]
            if tag == self.common_tag:
                for key in self.filter_search:
                    self.filter_search[key].addKey(word)
            else:
                self.filter_search[tag].addKey(word)
        return (self.pattern_list,self.filter_search)

    # init feature info 
    def initFeatureInfo(self,feature_string):
        # char based or word based
        if feature_string.find(FEATURE_WORD) != -1 \
            and feature_string.find(FEATURE_CHAR) != -1:
            logging.error("error: both char based and word based is forbiden.")
            return False
        self.word_based = False
        if feature_string.find(FEATURE_WORD) != -1:
            self.word_based = True
        # segment based
        self.segment_based = False
        if feature_string.find(FEATURE_SEGMENT) != -1 \
            or feature_string.find(FEATURE_POS) != -1 \
            or feature_string.find(FEATURE_WORD) != -1:
            self.segment_based = True
        # feature list
        self.feature_list = []
        tmp_list = feature_string.split(self.FEA_DIV) 
        for item in tmp_list:
            if item.find(self.FEA_SUBDIV) != -1:
                self.feature_list.append(item.split(self.FEA_SUBDIV))
            else:
                self.feature_list.append([item])
        return True
    # init feature representation type 
    def initRepTypeInfo(self,type_string):
        if type_string.find(self.BEGIN_TAG) == -1 or\
           type_string.find(self.INTER_TAG) == -1 or\
           type_string.find(self.OTHER_TAG) == -1:
            logging.error("error: must have B,I,O at least.")
            return False
        # check end tag
        if type_string.find(self.END_TAG) != -1:
            self.has_end_tag = True
        # check single tag
        if type_string.find(self.SINGLE_TAG) != -1:
            self.has_single_tag = True
        # set current end tag
        if self.has_end_tag:
            self.CUR_END_TAG = self.END_TAG
        else:
            self.CUR_END_TAG = self.INTER_TAG
    # read entity wrod list
    @staticmethod
    def ReadKeyValue(file_name):
        entity_hash = {}
        if os.path.exists(file_name) == False:
            return entity_hash
        fhandle = open(file_name)
        for line in fhandle:
            line  = line.rstrip()
            if line == "":
                continue
            tmp_list = line.split("\t")
            if len(tmp_list) < 2:
                continue
            entity = tmp_list[0]
            tag = tmp_list[1]
            if entity in entity_hash:
                continue
            entity_hash[entity] = tag
        fhandle.close()
        return entity_hash
    
    # read entity wrod list
    @staticmethod
    def ReadPairWord(file_name):
        ret_list = []
        if os.path.exists(file_name) == False:
            return ret_list
        fhandle = open(file_name)
        for line in fhandle:
            line  = line.rstrip()
            if line == "":
                continue
            tmp_list = line.split("\t")
            if len(tmp_list) < 2:
                continue
            pattern = tmp_list[0]
            tag = tmp_list[1]
            ret_list.append((pattern,tag))
        fhandle.close()
        return ret_list
    # tag_dict中相应位置做上标记
    '''#############util function#################'''
    # get word & position from tag dict 
    def mergeTagDictEx(self, content, dict1,dict2, all_merge=False):
        ret_dict  = {}
        for item in dict1:
            ret_dict[item] = dict1[item]
        # get labeled word list
        chunk_list = self.getChunkFromTag(content,dict2)
        chunk_pos = 0
        for (chunk, flag,tag) in chunk_list:
            word_len = len(chunk.decode("utf-8"))
            if all_merge or flag:
                self.markTag(ret_dict,chunk_pos,word_len,tag)
            chunk_pos += word_len
        return ret_dict

    # tag_dict中相应位置做上标记
    def markTag(self,tag_dict,begin,word_len,appendix=None):
        # search conflict
        inx = 0
        while inx < word_len:
            index = str(begin + inx) 
            inx += 1
            if index in tag_dict:
                return
        # make tag
        if appendix != None:
            app = self.TAG_DIV+appendix
        else:
            app = ""
        inx = 0
        while inx < word_len:
            index = str(begin + inx) 
            if index in tag_dict:
                inx += 1
                continue
            if inx == 0:
                if self.has_single_tag and word_len == 1:
                    tag_dict[index] = self.SINGLE_TAG+app
                else:
                    tag_dict[index] = self.BEGIN_TAG+app
            elif inx == word_len - 1:
                tag_dict[index] = self.CUR_END_TAG+app
            else:
                tag_dict[index] = self.INTER_TAG+app
            inx += 1

    # find out wrong word
    def filterByWord(self, string, tag):
        if tag in self.filter_search:
            (filter_result, tmp_none) = self.filter_search[tag].maxSearchEx(string, "utf-8")
            if len(filter_result) > 0:
                return True
        return False
    # restore chunk from tag dict
    def getChunkFromTag(self, content, entity_tag):
        content_uni = content.decode("utf-8")
        inx = 0
        curFlag = False
        bWord = "".decode("utf-8")
        chunk_list = []
        while inx < len(content_uni):
            un_char = content_uni[inx]
            str_inx = str(inx)
            if str_inx in entity_tag:
                next_flag = True
            else:
                next_flag = False
            if str(inx-1) in entity_tag:
                oldTag = entity_tag[str(inx-1)].split(self.TAG_DIV)[1]
            else:
                oldTag = "UNKNOWN"
                
            # find a B-, print the previous chunk
            if (str_inx in entity_tag) and (self.checkTagPrefix(entity_tag[str_inx],self.BEGIN_TAG)\
               or self.checkTagPrefix(entity_tag[str_inx],self.SINGLE_TAG)):
                if len(bWord) > 0:
                    chunk_list.append((bWord.encode("utf-8"),curFlag,oldTag))
                curFlag = next_flag
                bWord = "".decode("utf-8")
            elif curFlag != next_flag:
                # if flag changed,print the previous chunk    
                if len(bWord) > 0:
                    chunk_list.append((bWord.encode("utf-8"),curFlag,oldTag))
                curFlag = next_flag
                bWord = "".decode("utf-8")
            bWord += un_char
            inx += 1
        if curFlag:
            oldTag = entity_tag[str(len(content_uni)-1)].split("-")[1]
        else:
            oldTag = "UNKNOWN"
        if len(bWord) > 0:
            chunk_list.append((bWord.encode("utf-8"),curFlag,oldTag))
        return chunk_list

    def getTagFromCrfResult(self, line_list,column_id):
        tag_dict = {}
        cnt = 0
        for line in line_list:
            cur_cnt = cnt
            cnt += 1
            tmp_list = line.split("\t")
            if len(tmp_list) < column_id+1:
                continue
            if tmp_list[column_id] != self.OTHER_TAG:
                tag_dict[str(cur_cnt)] = tmp_list[column_id]
        return tag_dict

    @staticmethod
    def getContentFromCrfResult(line_list,column_id=0):
        content = ""
        for line in line_list:
            tmp_list = line.split("\t")
            if len(tmp_list) < column_id+1:
                break
            content += tmp_list[column_id] 
        return content
    # check prefix
    def checkTagPrefix(self,tag_string,prefix):
        if tag_string == prefix or tag_string.find(prefix+self.TAG_DIV) != -1:
            return True
        return False
    # is valid chunk
    def isValidChunk(self,tag_dict,begin,word_len):
        if word_len < 1:
            return False
        if not str(begin) in tag_dict:
            return False
        # not B- or S- begins
        if (not self.checkTagPrefix(tag_dict[str(begin)],self.BEGIN_TAG)) and \
           (not self.checkTagPrefix(tag_dict[str(begin)],self.SINGLE_TAG)):
            return False
        # check inter tag
        inx = 1
        while inx < (word_len - 1):
            inter = str(begin+inx)
            if not inter in tag_dict:
                #logging.debug("b=%d,inx=%d,word_len=%d"%(begin,inx,word_len))
                return False
            if not self.checkTagPrefix(tag_dict[inter],self.INTER_TAG):
                return False
            inx += 1
        # check end, skip when word_len = 1
        end_str = str(begin+word_len-1)
        if word_len > 1:
            if (not end_str in tag_dict) or (not self.checkTagPrefix(tag_dict[end_str],self.CUR_END_TAG)):
                return False
        # next must be another chunk
        next_str = str(begin+word_len)
        if (not next_str in tag_dict) or \
            self.checkTagPrefix(tag_dict[next_str],self.BEGIN_TAG) or\
            self.checkTagPrefix(tag_dict[next_str],self.SINGLE_TAG):
            return True
        else:
            return False
    # char index to word index
    def charIndexToWordIndex(self,char_pos,char_len):
        if not str(char_pos) in self.charword_map:
            return None
        (adj_start,tmp) = self.charword_map[str(char_pos)]
        pos = char_pos
        end = char_pos + char_len
        adj_len = 0
        while pos < end:
            if not str(pos) in self.charword_map:
                return None
            (tmp,word_len) = self.charword_map[str(pos)]
            adj_len += 1
            pos += word_len
        return (adj_start,adj_len)
    # get split tag
    def normalizeTag(self,old_tag):
        if old_tag.find(self.TAG_DIV):
            return old_tag
        tmp_list = old_tag.split(self.TAG_DIV)
        return tmp_list[1]
    # get ltp result
    @staticmethod
    def getLtpResult(ltpClient,content):
        (a,b,flag) = ltpClient.getSegment(content,1,2,0)
        segment_list = []
        if flag :
            tmp_list = ltpClient.getSegmentInfo(b)
            for word_item in tmp_list:
                (word, begin, str_len, pos_tag) = word_item
                segment_list.append((word,pos_tag))
        return segment_list
if __name__ == '__main__':
    tag_getter = GenerateTag()
    content = "公开资料显示，杨龙忠毕业于中南大学，是比亚迪总裁王传福的同学，西北纺织学院比亚迪三大创始人之一，不仅担任比亚迪股份公司副总裁，同时也是比亚迪集团公司副总裁。"
    tag_getter.resetTagger()
    tag_getter.mkTag(content)
    tag_getter.wordBasedTransform()
    print tag_getter.outputByCrfFormat()
    print tag_getter.transDictToTagstring(content, tag_getter.getFeatureDict(FEATURE_DICT))
