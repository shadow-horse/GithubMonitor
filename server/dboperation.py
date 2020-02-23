# -*- coding:utf-8 -*-

'''
扫描任务操作db的函数封装 
    说明：后台应用，不做SQL注入防护
'''
import sqlite3

class dboperation:
    def __init__(self):
        self.maindb = 'main.db'
        self.scantask = 'scantask'
    
    ########################################################
    '''
    操作main.db，插入创建的扫描任务信息
    '''
    def insertscantask(self,name,f_keys,s_keys,repo_keys,parent_id=0,states=0):
        conn = sqlite3.connect(self.maindb)
        cursor = conn.cursor()
        sql = "insert into scantask ( name,f_keys,s_keys,repo_keys,parent_id,states) values (?,?,?,?,?,?)"
        cursor.execute(sql,(name,f_keys,s_keys,repo_keys,parent_id,states))
        cursor.close()
        conn.commit()
        conn.close()
        print('insertscantask success......')
        
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
        每个扫描任务创建一个db，保存扫描任务的扫描结果
        表结构:
            status:标识是否需要屏蔽
        
    '''
    def createscantaskdb(self,id):
        dbname = "%s_scantask.db" % (id)
        conn = sqlite3.connect(dbname)
        #创建表格
        cursor = conn.cursor()
        
        sql = "create table if not exists scanlist("\
        + "id integer primary key autoincrement," \
        + "name text," \
        + "path text,"\
        + "sha text,"\
        + "html_url text,"\
        + "repo text,"\
        + "content text,"\
        + "status varchar(30)"\
        + ")"
        cursor.execute(sql)
        cursor.close()
        conn.commit()
        conn.close()
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
    
if __name__ == '__main__':
    
    db = dboperation()
#     db.createscantaskdb(2)
    values = db.selectscantask(2)
    print(values)
    db.openscanlist(2)
#     db.insertscanlist('test', 'http://www.baidu.com', 'sha1', 'html_url', 'repo', 'content')
    values = db.selectallscanlist()
    print(values)
    db.closescanlist() 
    
    