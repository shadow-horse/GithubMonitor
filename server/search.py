# -*- coding:utf-8 -*-

'''
创建扫描任务，并存储扫描结果
'''

import dboperation
import githubapi
import math
import dbscantask
import hashlib
import time
import datetime
import json
import requests
import config
requests.adapters.DEFAULT_RETRIES =5

class search:
            
    '''
    创建扫描任务
    1. 在main.db中插入扫描任务
    2. 创建id_scantask.db,并创建存储表
    3. 调用Github api查询结果
    
    '''
    def createshtask(self,name,f_keys,s_keys,repo_keys,parent_id=0):
        print('createshtask......')
        dbo = dboperation.dboperation()
        dbo.insertscantask(name,f_keys,s_keys,repo_keys,parent_id)
    
    def getshtaskinfo(self,id=0):
        print('getshtaskinfo.....')
        dbo = dboperation.dboperation()
        values = dbo.selectscantask(id)
        return values
    
    '''
    执行扫描任务，调用查询接口，保存至数据库中
    '''
    def executetask(self,id):
        values = self.getshtaskinfo(id)
        id = values[0][0]
        name = values[0][1]
        f_keys = values[0][2]
        s_keys = values[0][3]
        repo_keys = values[0][4]
        parent_id = values[0][5]
        status = values[0][6]
        
        #答应扫描的任务
        print('==============扫描任务=================')
        print('id:'+ str(id))
        print('name:' + name)
        print('f_keys:' + f_keys)
        print('s_keys'+ s_keys)
        print('repo_keys:'+repo_keys)
        print(parent_id)
        print(status)
        print('====================================')
        
        #判断扫描状态
        #判断是否存在parent_id，基于已有结果进行搜索
        #此处直接search code
        
        dataItems = []
        
        try:
            api = githubapi.githubapi()
            res = api.searchcode(f_keys)
            
            if not res:
                print('初始扫描异常，扫描结束')
                #设置扫描状态
                taskdb = dbscantask.dbscantask()
                taskdb.uptaskstatusByid(id,3)
                return False
         
            total_count = res['total_count']
            pages = math.floor(total_count/100) 
            print('扫描共%s条记录，分为%s页' % (total_count,pages))
            
            item = res['items']
            reponame=''
            for i in item:
                result = self.dealitem(i,id,f_keys,flag='0')
                if(result):
                    dataItems.append(i)
            
            #github最多返回1000条数据，默认每一页100条
            if(pages > 10):
                pages = 11
            else:
                pages = pages+1
            
            for i in range(2,pages):
                res = api.searchcode(f_keys,i)
                if not res:
                    continue
                item = res['items']
                for i in item:
                    result = self.dealitem(i,id,f_keys,flag='0')
                    if(result):
                        dataItems.append(i)
            
            #在该文件中搜索二级关键词
            for item in dataItems:
                self.dealsecitem(item, id, f_keys, s_keys, '1')
             
            #搜索仓库关键词
            reponame=''
            for item in dataItems:
                reponame = self.dealrepoitem(item, id, f_keys, repo_keys, '2',reponame)       
            #设置扫描状态
            taskdb = dbscantask.dbscantask()
            taskdb.uptaskstatusByid(id,2)
        except Exception as e:
            print(e)
            #设置扫描状态
            taskdb = dbscantask.dbscantask()
            taskdb.uptaskstatusByid(id,3)
        
        print("扫描结束")            
        return True
    
    #插入数据
    def insertdata(self,id,name,path,sha,html_url,repo_name,content,flag='0'):
        suffix = self.judgeFilesuffix(name)
        if(suffix == 'black'):
            return False
    
        dbitem = dboperation.dboperation()
        #打开数据库连接
        dbitem.openscanlist(id)
        
        #如果flag=1并且文件已经存在，则删除文件，重新插入
        if(self.md5isExist(id, sha, html_url) and (flag == '1')):
            dbitem.delescanlistBysha(sha,html_url)
        
        if(suffix == 'white'):
            dbitem.insertscanlist(name,path,sha,html_url,repo_name,content,'5')
        else:
            dbitem.insertscanlist(name,path,sha,html_url,repo_name,content,flag)
        #关闭数据库连接
        dbitem.closescanlist()
        return True
   
    def md5isExist(self,id,md5,htmlurl):
        db = dboperation.dboperation()
        result = db.md5isExist(id,md5,htmlurl)
        return result
    def htmlurlisExist(self,id,htmlurl):
        db = dboperation.dboperation()
        result = db.htmlurlisExist(id,htmlurl)
        return result
    
    def judgeFilesuffix(self,name):
        blacklist = ['.cache','.types','.ipynb','.tex','.resx','.wxss','.svg','.raw','.pgm','.ima','.pgm','.gemspec','.buildinfo','.gitignore','.css','.m3u','.classpath']
        whitelist = ['.java','.php','.ini','.conf','.properties','.c','.xml','.bak','.cpp','.sh','.py','.md','.csv','.sql','.log','.rb','.go','.h','.cc','.tsv','.pl']
        middlelist = ['.json','.html','.htm','.js','.ejs','.vue','.ts','.tsx','.jsx']
        
        for item in blacklist:
            if(name.endswith(item)):
                return 'black'
        
        for item in whitelist:
            if (name.endswith(item)):
                return 'white'
        
        return 'middle'
    
    #处理一级搜索结果    
    def dealitem(self,item,id,keys,flag='0'):  
        name = item['name']
        path = item['path']
        sha = item['sha']
        html_url = item['html_url']
        repo_name = item['repository']['full_name']
        #添加发现时间
        get_time = (datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        content = get_time +"  " + keys
        #根据文件后缀判断是否需要继续检查
        suffix = self.judgeFilesuffix(name)
        if(suffix == 'black'):
            return False
        
        #判断文件是否已经在数据库中减少搜索访问
        if(self.md5isExist(id, sha,html_url)):
            return False
     
        self.insertdata(id,name,path,sha,html_url,repo_name,content,flag)
        return True
    
    #处理二级搜索结果
    def dealsecitem(self,item,id,f_keys,keys,flag = '1'):
        if(keys == ''):
            return False
        name = item['name']
        path = item['path']
        sha = item['sha']
        html_url = item['html_url']
        repo_name = item['repository']['full_name']
        content = keys
        #根据文件后缀判断是否需要继续检查
        suffix = self.judgeFilesuffix(name)
        if(suffix == 'black'):
            return False
        
        rawsearch = githubapi.githubapi()
        s_keys_d = []
        s_keys_d = keys.split('|')
        for key in s_keys_d:
            if(key != ''):
                result = rawsearch.searchfilename(repo = repo_name,name= name,path=path,id=key)
                if result :
                    content = f_keys + '|' + key
                    self.insertdata(id,name,path,sha,html_url,repo_name,content,flag=1)
                    break
        return True
    #处理仓库搜索结果
    def dealrepoitem(self,item,id,f_keys,keys,flag = '2',reponame=''):
        if(keys == ''):
            return False
        name = item['name']
        path = item['path']
        sha = item['sha']
        html_url = item['html_url']
        repo_name = item['repository']['full_name']
        content = keys
        #根据文件后缀判断是否需要继续检查
        suffix = self.judgeFilesuffix(name)
        if(suffix == 'black'):
            return False
        if(reponame == repo_name):
            return repo_name
        
        rawsearch = githubapi.githubapi()
        repo_keys_d = []
        repo_keys_d = keys.split('|')
        for key in repo_keys_d:
            if(key !=''):
                repores = rawsearch.searchByrepo(repo_name,key)
                if(repores != False):
                    content = f_keys + '\t' + key
                    repoitem = repores['items']
                    for i in repoitem:
                        self.dealitem(i,id,content,flag=2)
        
        return repo_name
        
    '''
    定时扫描任务调用主要扫描新增问题，当检查到5个文件连续已经存在了则终止执行
    '''
    def timingtask(self,id):
        values = self.getshtaskinfo(id)
        id = values[0][0]
        name = values[0][1]
        f_keys = values[0][2]
        s_keys = values[0][3]
        repo_keys = values[0][4]
        parent_id = values[0][5]
        status = values[0][6]
        
        #MD5存在计算器，如果连续limit值则扫描结束
        counter = 0
        counterlimit= 10
       
        print('==============定时扫描任务=================')
        print('id:'+ str(id))
        print('name:' + name)
        print('f_keys:' + f_keys)
        print('s_keys'+ s_keys)
        print('repo_keys:'+repo_keys)
        print('========================================')
        #判断是否存在parent_id，基于已有结果进行搜索
        #此处直接search code
        dataItems = []

        try:
            api = githubapi.githubapi()
            res = api.searchcode(f_keys)
            
            if not res:
                print('定时扫描任务终止：异常终止')
                #设置扫描状态
                taskdb = dbscantask.dbscantask()
                taskdb.uptaskstatusByid(id,3)
                return False
         
            total_count = res['total_count']
            pages = math.floor(total_count/100)
            print('扫描共%s条记录，分为%s页' % (total_count,pages))
            
            item = res['items']
            reponame=''
            for i in item:
                if(counter > counterlimit):
                    break
                
                if(self.md5isExist(id, i['sha'],i['html_url'])):
                    print('重复条目：'+i['path'])
                    counter = counter + 1
                else:
                    counter = 0
                result = self.dealitem(i,id,f_keys,flag='0')
                if(result):
                    dataItems.append(i)
            #github最多返回1000条数据，默认每一页100条
            if(pages > 10):
                pages = 11
            else:
                pages = pages+1
            for i in range(2,pages):
                if(counter > counterlimit):
                    break
                res = api.searchcode(f_keys,i)
                if not res:
                    print('定时扫描任务异常：'+ res)
                    continue
                item = res['items']
                for i in item:
                    if(counter > counterlimit):
                        break
                    if(self.md5isExist(id, i['sha'],i['html_url'])):
                        print('重复条目：'+i['path'])
                        counter = counter + 1
                    else:
                        counter = 0
                    result = self.dealitem(i,id,f_keys,flag='0')
                    if(result):
                        dataItems.append(i)
            #在该文件中搜索二级关键词
            for item in dataItems:
                self.dealsecitem(item, id, f_keys, s_keys, '1')
             
            #搜索仓库关键词
            reponame = ''
            for item in dataItems:
                reponame = self.dealrepoitem(item, id, f_keys, repo_keys, '2',reponame)
                   
            #设置扫描状态
            taskdb = dbscantask.dbscantask()
            taskdb.uptaskstatusByid(id,2)
        except Exception as e:
            print('定时扫描任务终止：异常终止')
            print(e)
            #设置扫描状态
            taskdb = dbscantask.dbscantask()
            taskdb.uptaskstatusByid(id,3)
        if(counter > counterlimit):
            print('重复条目已经大于临界值')
        print("定时扫描任务结束")            
        return True
 
    '''
    修改循环扫描逻辑，循环监控只针对一级扫描关键词监控新增的文件，为了减少误报和漏报率以及工作投入，对新增文件的监控属于最有效的办法
    '''
    def monitorNewFiletask(self,id):
        values = self.getshtaskinfo(id)
        id = values[0][0]
        name = values[0][1]
        f_keys = values[0][2]
        s_keys = values[0][3]
        repo_keys = values[0][4]
        parent_id = values[0][5]
        status = values[0][6]
        
        #MD5存在计算器，如果连续limit值则扫描结束
        counter = 0
        counterlimit= 10
       
        print('==============定时扫描任务=================')
        print('id:'+ str(id))
        print('name:' + name)
        print('f_keys:' + f_keys)
        print('s_keys'+ s_keys)
        print('repo_keys:'+repo_keys)
        print('========================================')
        #判断是否存在parent_id，基于已有结果进行搜索
        #此处直接search code
        try:
            api = githubapi.githubapi()
            res = api.searchcode(f_keys)
            
            if not res:
                print('定时扫描任务终止：异常终止')
                #设置扫描状态
                taskdb = dbscantask.dbscantask()
                taskdb.uptaskstatusByid(id,3)
                return False
         
            total_count = res['total_count']
            pages = math.floor(total_count/100)
            print('扫描共%s条记录，分为%s页' % (total_count,pages))
            
            #消息告警
            
            item = res['items']
            reponame=''
            for i in item:
                if(counter > counterlimit):
                    break
                if(self.htmlurlisExist(id,i['html_url'])):
                    print('重复条目：'+i['path'])
                    counter = counter + 1
                else:
                    counter = 0
                    result = self.dealitem(i,id,f_keys,flag='0')
                    
            #github最多返回1000条数据，默认每一页100条
            if(pages > 10):
                pages = 11
            else:
                pages = pages+1
            for i in range(2,pages):
                if(counter > counterlimit):
                    break
                res = api.searchcode(f_keys,i)
                if not res:
                    print('定时扫描任务异常：'+ res)
                    continue
                item = res['items']
                for i in item:
                    if(counter > counterlimit):
                        break
                    if(self.htmlurlisExist(id,i['html_url'])):
                        print('重复条目：'+i['path'])
                        counter = counter + 1
                    else:
                        counter = 0
                        result = self.dealitem(i,id,f_keys,flag='0')
            #设置扫描状态
            taskdb = dbscantask.dbscantask()
            taskdb.uptaskstatusByid(id,2)
        except Exception as e:
            print('定时扫描任务终止：异常终止')
            print(e)
            #设置扫描状态
            taskdb = dbscantask.dbscantask()
            taskdb.uptaskstatusByid(id,3)
        if(counter > counterlimit):
            print('重复条目已经大于临界值')
        print("定时扫描任务结束")            
        return True    
if __name__ == '__main__':
    print('search......')
#     sh = search()
#     #创建扫描任务
# #     sh.createshtask('扫描test.xyz', 'test.xyz', 'password', 'password')    
#     values = sh.getshtaskinfo(2)
#     sh.executetask(2)