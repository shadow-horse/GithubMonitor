# -*- coding:utf-8 -*-

'''
定时扫描任务:每隔固定时间则遍历执行
目的：监控新增
'''

import dboperation
import githubapi
import math
import dbscantask
import search
import time
import datetime

class timingtask:
    def __init__(self):
        #设置时间间隔：分钟
        self.timeinterval = 12 * 60 * 60
        
    def gettasklist(self):
        db = dbscantask.dbscantask()
        tasklist = db.getalltasklist()
        return tasklist
    
    def executeBytaskid(self,item):
        #判断扫描任务是否处理扫描状态
#         if(item['states'] == '1'):
#             return False

        db = dbscantask.dbscantask()
        db.uptaskstatusByid(item['id'],'1')
        
        sea =  search.search()
        #监控文件md5的变化
#         sea.timingtask(item['id'])
        #监控文件是否新增  
        sea.monitorNewFiletask(item['id'])
        return True
                
    def run(self):
        while(True):
            tasklist = self.gettasklist()
            for item in tasklist:
                self.executeBytaskid(item)
            get_time = (datetime.datetime.now()).strftime('%H')
            int_time = int(get_time)
            if(int_time <6 or int_time >23):
                continue
            else:
                hours = 23-int_time
                print("please wait %s hours" % (hours))
                seconds = (23-int_time) * 60 * 60 
                time.sleep(seconds)       
        
    
if __name__ == '__main__':
    task = timingtask()
    task.run()    