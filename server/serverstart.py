# -*- coding:utf-8 -*-
'''
快速创建http服务，监听服务请求

FastAPI是一个现代的、快速（高性能）的web框架
pip3 install fastapi 
pip3 install uvicorn
'''
from pydantic import BaseModel
from fastapi import FastAPI
import dbscantask
import dboperation
import json
import threading
import search

app = FastAPI()
 
threads = []
threadsid = 1
'''
获取扫描任务列表
参数：
    current:第几页
    pageSize:每页多少条数据
    sorter:排序
返回：
    {"data":[
        {
        "key":id,
        "name":"扫描任务",
        "f_keys":"www.test.com.cn",
        "s_keys":"password",
        "repo_keys":"username && password",
        "parent_id":"10001",
        "states":0
        }
    ],"total":100,"success":true,"pageSize":"10","current":1}
'''

@app.get('/monitor/task?')
async def getmonitortask(current:int,pageSize:int,name:str=None,f_keys:str=None,s_keys:str=None,repo_keys:str=None,parent_id:str=None):
    task = dbscantask.dbscantask()
    taskdata = task.getscanlist(current=current, pageSize=pageSize,name=name,f_keys=f_keys,s_keys=s_keys,repo_keys=repo_keys,parent_id=parent_id)
    data = {}
    data['data'] = taskdata
    total = task.getscanlistnums()
    data['total']=total
    data['success']=True
    data['pageSize']=pageSize
    data['current']=current
    
    
    return data

 
class dataItem(BaseModel):
    id:int=None
    key:list=None
    name:str=''
    f_keys: str=''
    s_keys: str=''
    repo_keys: str=''
    parent_id: str='0'
    states: str='0'
    method: str='0'
    
'''
添加扫描任务：
    参数：dataItem
    method:post
    返回：{"id":101,"name":"2","f_keys":"2","s_keys":"2","repo_keys":"2","parent_id":"2","states":"2"}
    
    method:delete
    返回：{"list":[{"id":100,"name":"1","f_keys":"1","s_keys":"1","repo_keys":"1","parent_id":"1","states":"0"}],"pagination":{"total":101}}
    
'''   
    
@app.post('/monitor/task')
async def addmonitortask(req_data:dataItem):
    db = dbscantask.dbscantask()
    #创建扫描任务
    if(req_data.method == 'post' and req_data.id == None):
        #插入扫描任务
        id = db.insertscantask(name=req_data.name,f_keys=req_data.f_keys,s_keys=req_data.s_keys,repo_keys=req_data.repo_keys,parent_id=req_data.parent_id)
        #创建扫描任务数据库
        db.createscantaskdb(id)
        
        jsonitem={}
        jsonitem['id'] = id
        jsonitem['name'] = req_data.name
        jsonitem['f_keys'] = req_data.f_keys
        jsonitem['s_keys'] = req_data.s_keys
        jsonitem['repo_keys'] = req_data.repo_keys
        jsonitem['parent_id'] = req_data.parent_id
        jsonitem['states'] = 0
        return jsonitem
    elif (req_data.method == 'post' and req_data.id != None):
        #更新扫描任务
        id = db.updatescantask(id=req_data.id,name=req_data.name,f_keys=req_data.f_keys,s_keys=req_data.s_keys,repo_keys=req_data.repo_keys,parent_id=req_data.parent_id,states=req_data.states)
        jsonitem={}
        jsonitem['id'] = id
        jsonitem['name'] = req_data.name
        jsonitem['f_keys'] = req_data.f_keys
        jsonitem['s_keys'] = req_data.s_keys
        jsonitem['repo_keys'] = req_data.repo_keys
        jsonitem['parent_id'] = req_data.parent_id
        jsonitem['states'] = 0
        return jsonitem
    elif(req_data.method == 'delete'):
        db.deletescanlist(req_data.id)
        jsonitem={}
        jsonitem['list'] = db.getscanlist()
        total = {}
        total['total'] = db.getscanlistnums()
        jsonitem['pagination']=total
        return jsonitem
    
    elif(req_data.method == 'remove'):
        jsonitem={}
        jsonitem['list']=[]
        total = {}
        total['total'] = db.getscanlistnums()
        jsonitem['pagination'] = total
        db.removescanlist(req_data.key)
        return jsonitem
 


class runtaskThread (threading.Thread):
    def __init__(self, threadID, id):
        threading.Thread.__init__(self)
        print(threadID)
        print(id)
        self.threadID = threadID
        self.id = id
    def getid(self):
        return self.id
    def run(self):
        #启动扫描
        runtask = search.search()
        runtask.executetask(self.id)
        #设置扫描结束状态
        db = dbscantask.dbscantask()
        db.uptaskstatusByid(self.id,2);

'''
执行扫描任务
'''
@app.post('/scantask/runtask')
async def runscantask(req_data:dataItem): 
    if(req_data.method == 'runtask'):
        db = dbscantask.dbscantask()
        task = db.queryscanlistByid(req_data.id);
        #判断该任务是否在扫描中,status = 1处于扫描中，如果处于扫描中，则不进行操作
        if (len(task) >0 and task[0][6] == 1):
            return {}
        
        #创建子线程，开启扫描任务
        try:
            print("创建子线程")
            thread1 = runtaskThread(req_data.id,req_data.id)
            thread1.start()
            threads.append(thread1)
        except Exception as e:
            print(e)
            return {'status':'failed','message':'runtaskThread exception'}
        #更新扫描状态
        db.uptaskstatusByid(req_data.id,1);
        return {'status':'success','message':'run success'}
    else:
        return {'status':'success','message':''}

'''
获取扫描任务列表
'''
@app.post('/scantask/tasklist')
async def gettasklist(method:str=None):
    task = dbscantask.dbscantask()
    taskdata = task.getscanlist()
    return taskdata


class scanlistItem(BaseModel):
    id:str=None
    taskid:str=None
    scanlistid:str=None
    status:str=None
    method:str=None
'''
扫描任务scanlist
'''
@app.post('/scanlist/list')
async def getScanlist(req_data:scanlistItem):
    print(req_data.id)
    db = dboperation.dboperation()
    db.openscanlist(req_data.id)
    values=[]
    values = db.selectscanlistBystatus(req_data.status)
    db.closescanlist()
    return values

'''
标记处理结果
'''
@app.post('/scanlist/deleteid')
async def updateScanlistStatus(req_data:scanlistItem):
    db = dboperation.dboperation()
    db.openscanlist(req_data.taskid)
    db.updatescanlistByid(req_data.scanlistid,req_data.status);
    db.closescanlist()

'''
所有未待处理的标记为忽略
'''    
@app.post('/scanlist/updateallignore')
async def updateallignore(req_data:scanlistItem):
    db = dboperation.dboperation()
    db.openscanlist(req_data.id)
    db.updateallignore(req_data.status);
    db.closescanlist()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=8080,
                workers=1)
    