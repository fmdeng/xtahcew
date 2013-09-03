#!/usr/bin/python
#-*-coding:utf-8-*-
import sys,json,types
class MyEncoder(json.JSONEncoder):
    def default(self,obj):
        #convert object to a dict
        d = {}
        d['__class__'] = obj.__class__.__name__
        d['__module__'] = obj.__module__
        d.update(obj.__dict__)
        return d

class MyDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self,object_hook=self.dict2object)
    def dict2object(self,d):
        #convert dict to object
        if '__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = __import__(module_name, fromlist=class_name)
            class_ = None
            try:
                class_ = getattr(module,class_name)
                #print module,class_
            except AttributeError,NameError:
                print module_name,class_name,"#####key wrong###"
            #if isinstance(class_,types.ModuleType):
            #    class_ = getattr(class_,class_name)
            args = dict((key.encode('ascii'), value) for key, value in d.items()) #get args
            if class_ != None and callable(class_): 
                inst = class_() #create new instance
                for item in d:
                    inst.__dict__[item] = d[item]
            else:
                inst = d
                print "can not init class:",d
        else:
            inst = d
        return inst
'''
module_name is in the format: xxx.xxx.xxx.classname
the fucntion is get the <classname> and return
'''
BUILTIN_TAG="__builtin__"
BUILTIN_MAP={"unicode":types.UnicodeType,"string":types.StringType,"float":types.FloatType,"int":types.IntType,"list":types.ListType}
def getClassInstance(class_path):
    module_info = class_path.split(".")
    module_len = len(module_info) -1
    modulename = ( ".".join(module_info[:module_len]))
    classname = module_info[-1] 
    if modulename == BUILTIN_TAG:
        return BUILTIN_MAP[classname]
    else:
        module_instance  = __import__(modulename, fromlist=classname)
        return getattr(module_instance, classname)

def whoami():
    return sys._getframe(1).f_code.co_name
