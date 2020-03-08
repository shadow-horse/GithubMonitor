# -*- coding:utf-8 -*-

'''
扫描任务操作db的函数封装 
    说明：后台应用，不做SQL注入防护
'''
import sqlite3
from numpy.distutils.from_template import item_re

class dboperation:
    def __init__(self):
        self.maindb = 'main.db'
        self.scantask = 'scantask'
    
    ########################################################
   
        
    '''
    查询main.db，返回创建任务列表
    '''
    def selectscantask(self,id=0):
        conn = sqlite3.connect(self.maindb)
        cursor = conn.cursor()       
        sql = ''
        if id == 0:
           sql =  'select * from scantask'
        else:
            sql = 'select * from scantask where id='+str(id)
        cursor.execute(sql)
        values = cursor.fetchall()
        return values
        
    
    ########################################################
    
    
    '''
    保存扫描结果前，先打开存储DB，操作完成后关闭存储DB
    '''
    def openscanlist(self,id):
        self.scanlistdb = "%s_scantask.db" % (id)
        self.slconn = sqlite3.connect(self.scanlistdb)
        self.slcursor = self.slconn.cursor()
        
    def closescanlist(self):
        self.slcursor.close()
        self.slconn.commit()
        self.slconn.close()
        
    '''
    插入扫描的每一条记录
    '''        
    def insertscanlist(self,name,path,sha,html_url,repo,content):
        
        #判断数据是否存在
        sql = "select id from scanlist where sha = ?"
        self.slcursor.execute(sql,[(sha)])
        values = self.slcursor.fetchall()
        if len(values) != 0:
            print('数据已经存在 %s......' % sha)
            return False
        
        sql = "insert into scanlist(name,path,sha,html_url,repo,content,status) values(?,?,?,?,?,?,?);"
        self.slcursor.execute(sql,(name,path,sha,html_url,repo,content,'0'))
        return True
    
    '''
    获取扫描任务的扫描结果
    '''
    def selectallscanlist(self):
        sql = "select * from scanlist"
        self.slcursor.execute(sql)
        values = self.slcursor.fetchall()
        return values
    
    def selectscanlist(self,sha):
        sql = "select * from scanlist where sha =?"
        self.slcursor.execute(sql,[(sha)])
        values = self.slcursor.fetchall()
        return values
    '''
    更新一条扫描结果的状态，是否屏蔽
    status:
        0:未处理
        1:不需要处理，屏蔽该条记录
    '''
    def updatescanlist(self,sha,status):
        sql = "update scanlist set status=? where sha=?"
        self.slcursor.execute(sql,(status,sha))
        return True
    
    '''
    删除某条记录
    '''
    def deletescanlist(self,id):
        sql = "delete from scanlist where id =?"
        self.slcursor.execute(sql,[(id)])
        return True
        
    
if __name__ == '__main__':
    
    db = dboperation()
    values = db.selectscantask(2)
    print(values)
    db.openscanlist(2)
#     db.insertscanlist('test', 'http://www.baidu.com', 'sha1', 'html_url', 'repo', 'content')
    values = db.selectallscanlist()
    for item in values:
        print(item)
#     
#     for i in range(1,64):
#         db.deletescanlist(str(i))
    
    db.closescanlist() 
    
    