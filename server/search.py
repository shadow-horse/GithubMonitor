# -*- coding:utf-8 -*-

'''
创建扫描任务，并存储扫描结果
'''

import dboperation
import githubapi
import math

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
        
        #创建扫描任务db及表
        dbo = dboperation.dboperation()
        dbo.createscantaskdb(id)
        
        #判断扫描状态
        print(f_keys)
        ii = 0
        api = githubapi.githubapi()
        res = api.searchcode(f_keys)
        if not res:
            print('初始扫描异常，扫描结束')
            return False
         
        total_count = res['total_count']
        pages = math.floor(total_count/100)
        print('扫描共%s条记录，分为%s页' % (total_count,pages))
        
        item = res['items']
        for i in item:
            ii = ii + 1
            print('第%s条扫描结果' % (ii))
            self.dealitem(i,id,s_keys)
        
#         for i in range(2,pages+1):
#             res = api.searchcode(f_keys,i)
#             
#             if not res:
#                 print('扫描任务扫描完成，受限于1000条扫描结果')
#                 break
#             
#             print('第%s页' % (i))
#  
#             item = res['items']
#             for i in item:
#                 ii = ii + 1
#                 print('第%s条扫描结果' % (ii))
#                 self.dealitem(i)
         
                    
        return True
    
    
    def dealitem(self,item,id,s_keys='',repo_keys=''):
        name = item['name']
        path = item['path']
        sha = item['sha']
        html_url = item['html_url']
        repo_name = item['repository']['full_name']
        content = ''
        
        print(name)
        print(path)
        print(sha)
        print(html_url)
        print(repo_name)
        
        dbitem = dboperation.dboperation()
        #打开数据库连接
        dbitem.openscanlist(id)
        
        if(s_keys == ''):
            dbitem.insertscanlist(name,path,sha,html_url,repo_name,content)
        else:
            rawsearch = githubapi.githubapi()
            content = rawsearch.getkeywords(html_url,s_keys)
            if content !='' :
                dbitem.insertscanlist(name,path,sha,html_url,repo_name,content)
            else:
                print('seconde keys search is null ' )
            
        #关闭数据库连接
        dbitem.closescanlist()        
        return True

if __name__ == '__main__':
    print('search......')
    sh = search()
    #创建扫描任务
#     sh.createshtask('扫描vmic.xyz', 'vmic.xyz', 'password', 'password')    
    values = sh.getshtaskinfo(2)
    print(values[0])    
    sh.executetask(2)