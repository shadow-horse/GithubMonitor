# -*- coding:utf-8 -*-

'''
定时扫描任务:每隔固定时间则遍历执行
'''

import dboperation
import githubapi
import math
import dbscantask
import search
import time



class timingtask:
    def __init__(self):
        #设置时间间隔：分钟
        self.timeinterval = 60 * 60 * 2
        
    def gettasklist(self):
        db = dbscantask.dbscantask()
        tasklist = db.getalltasklist()
        return tasklist
    
    def executeBytaskid(self,item):
        #判断扫描任务是否处理扫描状态
        if(item['states'] == '1'):
            return False
        
        db = dbscantask.dbscantask()
        db.uptaskstatusByid(item['id'],'1')
        
        sea =  search.search()
        sea.executetask(item['id'])
        return True
    
    def run(self):
        while(True):
            befortime = time.time()
            tasklist = self.gettasklist()
            for item in tasklist:
                self.executeBytaskid(item)
            
            aftertime = time.time()
            interval = aftertime - befortime
            if(interval < self.timeinterval):
                print('需要继续等待：')
                print(self.timeinterval - interval)
                time.sleep(self.timeinterval - interval)
                
           
        
    
if __name__ == '__main__':
    task = timingtask()
    task.run()    