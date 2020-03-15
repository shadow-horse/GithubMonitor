# -*- coding:utf-8 -*-

'''
创建扫描任务，并存储扫描结果
'''

import dboperation
import githubapi
import math
import dbscantask

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
        ii = 0
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
            pages = math.floor(total_count/100) + 1
            print('扫描共%s条记录，分为%s页' % (total_count,pages))
            
            item = res['items']
            reponame=''
            for i in item:
                ii = ii + 1
                reponame = self.dealitem(i,id,f_keys,s_keys,repo_keys,reponame=reponame)
            
            for i in range(2,pages+1):
                res = api.searchcode(f_keys,i)
             
                if not res:
                    continue
                item = res['items']
                for i in item:
                    ii = ii + 1
                    reponame = self.dealitem(i,id,f_keys,s_keys,repo_keys,reponame=reponame)
                    
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
        dbitem = dboperation.dboperation()
        #打开数据库连接
        dbitem.openscanlist(id)
        dbitem.insertscanlist(name,path,sha,html_url,repo_name,content,flag)
        #关闭数据库连接
        dbitem.closescanlist()
        return True
   
    def md5isExist(self,id,md5):
        db = dboperation.dboperation()
        result = db.md5isExist(id,md5)
        return result
    
    def dealitem(self,item,id,f_keys,s_keys='',repo_keys='',flag='0',reponame=''):  
        name = item['name']
        path = item['path']
        sha = item['sha']
        html_url = item['html_url']
        repo_name = item['repository']['full_name']
        content = f_keys
        
        #判断文件是否已经在数据库中减少搜索访问
        if(self.md5isExist(id, sha)):
            print('文件存在: ' + path)
            return repo_name
        
        rawsearch = githubapi.githubapi()
        #如果存在二级搜索关键词
        if(s_keys !=''):
            #二级搜索关键词需要按照|拆分分别去扫描
            s_keys_d = []
            s_keys_d = s_keys.split('|')
            for key in s_keys_d:
                if(key != ''):
                    result = rawsearch.searchfilename(repo = repo_name,name= name,path=path,id=key)
                    if result :
                        content = f_keys + '\r\n' + key
                        self.insertdata(id,name,path,sha,html_url,repo_name,content,flag=1)
        
        
        #搜索仓库搜索关键词
        #判断仓库是否已经搜索过reponame为上一次调用返回的仓库名称

        if (repo_keys !='' and reponame != repo_name):
            print('搜索仓库'+repo_name)
            #仓库关键词按照|拆分
            repo_keys_d = []
            repo_keys_d = repo_keys.split('|')
            for key in repo_keys_d:
                if(key !=''):
                    repores = rawsearch.searchByrepo(repo_name,key)
                    if(repores != False):
                        content = f_keys + '\r\n' + key
                        repoitem = repores['items']
                        for i in repoitem:
                            self.dealitem(i,id,f_keys=content,s_keys='',repo_keys='',flag=2)
        
        
                  
        if(s_keys == '' and repo_keys == ''):
            content = f_keys
            self.insertdata(id,name,path,sha,html_url,repo_name,content,flag)
     
        return repo_name

if __name__ == '__main__':
    print('search......')
#     sh = search()
#     #创建扫描任务
# #     sh.createshtask('扫描test.xyz', 'test.xyz', 'password', 'password')    
#     values = sh.getshtaskinfo(2)
#     sh.executetask(2)