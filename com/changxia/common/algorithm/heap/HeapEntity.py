#!/usr/bin/python
#-*-coding:utf-8-*-
import random
'''
HeapEntity is base class for some class which need use 
Heap Data structure

'''

class HeapEntity:

    def __init__(self, score=0):
        self.score = score
    
    
    def getKey(self):
        return str(self.score)
        #return str(int(random.random() * 100))
    '''
    setter/getter for score
    '''
    def getScore(self):
        return self.score
    
    def setScore(self,score):
        self.score = score
    
    '''
    return 0 if score is equal
           1 bigger
           -1 smaller
    '''
    def compare(self, heap_entity):
        if self.score < heap_entity.getScore() :
            return -1
        if self.score > heap_entity.getScore():
            return 1
        return 0
    def __str__(self):
        return str(self.score)
    
    '''
        序列化可以存入redis 不能包含<tab>
    '''
    def serialize(self):
        return str(self.score)
    
    '''
      从redis里面序列化出来
    '''
    def unserialize(self, redis_str):
        self.score = int(redis_str)
        
    '''
      衰减函数,默认是没有实现的
    '''
    def decay(self):
        pass

if __name__=="__main__":

    heap_ent = HeapEntity(1) 
    heap_ent_two = HeapEntity(3)
    heap_ent_three = HeapEntity(1)
    print heap_ent.compare(heap_ent_two)
    print heap_ent.compare(heap_ent_three)
    print heap_ent
