#!/usr/bin/python
#-*-coding:utf-8-*-
from HeapEntity import *
'''
HeapOperator的主要作用是获得top n 的实体(HeapEntity)
    HeapEntity(HeapEntity.py) 的子类必须实现compare(), serialize, unserialize接口，并且在serialize的结果中不能用到
    tab。
基本用法：

  STEP 1
    #设置堆大小是3，SMALLEAST_HEAP_TYPE 的意思是我们希望获得最小的3个元素
    #深入一点讲，我们的堆是一个大顶堆，第一个元素一定是堆中最大的
    heapoperator = HeapOperator( 3, HeapOperator.SMALLEAST_HEAP_TYPE) 

  STEP 2
    #生成一个entity
    entity = HeapEntity(5)
    heapoperator.push(entity)
  重复步骤 2若干次

  STEP 3 转换为redis可存储格式
    s = heapoperator.serialize()
    save s to redis
  
  STEP 4 从redis中读取

    heapoperator = HeapOperator() 
    #s 是从redis里获得的数据， "HeapEntity" 是我们存储的类元素
    heapoperator.unserialize( s, "HeapEntity")

'''



class HeapException(Exception):
    def __init__(self,msg):
        Exception.__init__(self)
        self.message = msg


class HeapOperator:
    SMALLEAST_HEAP_TYPE = -1 #保存最小的数据， 大顶堆
    BIGGEST_HEAP_TYPE = 1    #保存最大的几个数据， 小顶堆

    def __init__(self, size = 100, heap_type = SMALLEAST_HEAP_TYPE, decay=False):
        self.size = size
        self.heap_type = heap_type
        self._entity_array = []
        self._dic_key = {}
        self.need_decay = decay

    '''
        将堆的元素系列化，转换为string, 可以存入redis
    '''
    def serialize(self):
        tmp_str = ""
        #serialize size
        tmp_str =  str(self.size)
        #serialize type
        tmp_str = tmp_str + "\t" + str(self.heap_type)
        #serialize _entity_array

        for item in self._entity_array:
            tmp_str = tmp_str + "\t" + item.serialize()    
        return tmp_str
    '''

    '''
    def unserialize(self, redis_str, entity_type):
        self._entity_array = []
        object_info = redis_str.split("\t")
        if len(object_info) < 2:
            raise HeapException("unserialize wrong , since it has not size or heap_type")
        self.size = int(object_info[0])
        self.heap_type = int(object_info[1])
        index = 0
        for item in object_info[2:]:
            entity = globals()[entity_type]()
            entity.unserialize(item)
            self._entity_array.append(entity)
            if index <> 0 :
                self._dic_key[entity.getKey()] =  index
            index = index + 1


    def printArray(self):
        return_str = ""
        count = 0
        for item in self._entity_array:
            if count <> 0 :
                #print item,
                if cmp(return_str, "") <> 0:
                    return_str = return_str + "\t" + str(item)
                else:
                    return_str = str(item)
            count = count + 1
        #print ""
        return return_str
    
    '''
        add, 当数据小于self.size的时候，我们直接将数据添加到堆里面，并且build堆
        否则，我们和堆的第一个元素比较，如果比堆的顶元素大，我们直接放弃，否则替换
        堆的顶部元素，再调整堆
        
    '''
    def push(self, item):
        update = False
        if self.need_decay == True:
            item.decay()
            for pre_item in self._entity_array:
                pre_item.decay()
        if item.getKey() in self._dic_key:
            return
        if update == True or self.need_decay == True:
            self.buildHeap()
        if update == True:
            return
        if self.getHeapSize() == 0:
            self._entity_array.append(item)
        if self.getHeapSize() < self.size + 1:
            self._entity_array.append( item)
            self.buildHeap()
            self._dic_key[item.getKey()] = 1
        else:
            if self.compare( self.get(1), item ) > 0 :
                return
            else:
                self.set(1, item)
                self._dic_key[item.getKey()] = 1
                self.heaplify(1)

    '''
        sort algorithm
    '''
    def heapSort(self):
        result = []
        self.buildHeap()
        while self.getHeapSize() > 1:
            result.append(self.get(1))
            self.set(1, self.get(self.getHeapSize() -1))
            self._entity_array.pop()
            self.heaplify(1)
        return result

    def buildHeap(self):
        for i in xrange(0, (self.getHeapSize() -1 )/2 ):
            self.heaplify( (self.getHeapSize() -1)/2 - i)

    
    '''
    assume the entity_one, entity_two has function compare
    '''
    def compare(self, entity_one, entity_two):
        try:
            return_result =  entity_one.compare(entity_two)
        except:
            raise HeapException( "we want to compare two entity, but they has not function named compare")
        return return_result * self.heap_type

    '''
        调整第i个位子的entity, 使得其满足第i位置上的数据都比子节点大
    '''
    def heaplify(self, i):
        left_index = -1
        right_index = -1
        try:
            left_index = self.left(i)
            right_index = self.right(i)
        except:
            return
        largest = i
        try: #sometimes right child doesn't exists
            if self.compare( self.get(i), self.get(left_index) ) < 0:
                largest = i
            else:
                largest = left_index

            if self.compare(self.get(largest), self.get(right_index)) > 0:
                largest = right_index
        except Exception ,e:
            pass
        if largest == i:
            return
        else:
            #exchange i and largest
            tmp = self.get(i)
            self.set(i, self.get(largest ))
            self.set(largest, tmp)
            self.heaplify(largest)


    '''
        just copy the data to self._entity_array
    '''
    def setHeap(self, data):
        self._entity_array = []
        self._entity_array.append(data[0])
        for item in data:
            self._entity_array.append(item)
    
    '''
        to get the value with the index i
    '''
    def get(self, i):
        if self.getHeapSize() -1  < i:
            raise HeapException("we want to get the index : %d, but the real size of heap is %d"%(i,self.getHeapSize()))
        return self._entity_array[i]

    '''
        to set the value with the index i
    '''
    def set(self, i, value):
        if self.getHeapSize() -1  < i:
            raise HeapException("we want to set the index : %d, but the real size of heap is %d"%(i,self.getHeapSize()))
        self._entity_array[i] = value

    '''
        get the real size of the heap
    '''
    def getHeapSize(self):
        return len(self._entity_array)

    '''
        get the capacity of the heap
    '''
    def getCapacity(self):
        return self.size


    def parent(self, i):
        if self.getHeapSize() -1  < i:
            raise HeapException("we want to search the parent of child : %d, but the real size of heap is %d"%(i,self.getHeapSize()))
        return i/2

    def left(self, i ):
        if self.getHeapSize() -1  < i:
            raise HeapException("we want to search the left child of parent : %d, but the real size of heap is %d"%(i,self.getHeapSize()))
        return i * 2


    def right(self, i):
        if self.getHeapSize() -1  < i:
            raise HeapException("we want to search the right child of parent : %d, but the real size of heap is %d"%(i,self.getHeapSize()))
        return i * 2 + 1
        

    

if __name__=="__main__":
    
    data = [73, 30, 4, 70, 13, 21, 19, 91, 1, 91]
    ent_array = []
    for item in data:
        ent_array.append( HeapEntity(item) )
    heapoperator_org = HeapOperator(100, HeapOperator.BIGGEST_HEAP_TYPE)
    heapoperator_org.setHeap(ent_array)
    s = heapoperator_org.serialize()
    print "serialize data:"
    print s
    heapoperator = HeapOperator()
    heapoperator.unserialize(s, "HeapEntity")
    #heapoperator = json.loads(s)
    heapoperator.printArray()
    result = heapoperator.heapSort()
    print "ORINAL data"
    for item in data:
        print item,
    print ""
    print "SORTED RESULT"
    for item in result:
        print item,
    print ""
    heapoperator = HeapOperator(3, HeapOperator.SMALLEAST_HEAP_TYPE)
    for item in ent_array:
        heapoperator.push(item)
    print "TOP THREE"
    heapoperator.printArray()
