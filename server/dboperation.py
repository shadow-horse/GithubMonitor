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
        插入每一条扫描记录
        参数说明：
       flag:
           0:一级搜索词搜索结果
           1:二级搜索词搜索到
           2:仓库搜索词搜索到
           3:标识为误报
           4:标识为需要处理
    '''     
    def insertscanlist(self,name,path,sha,html_url,repo,content,flag='0'):
        
        #判断数据是否存在
        sql = "select id from scanlist where sha = ?"
        self.slcursor.execute(sql,[(sha)])
        values = self.slcursor.fetchall()
        if len(values) != 0:
            print('数据已经存在 %s......' % sha)
            return False
        
        sql = "insert into scanlist(name,path,sha,html_url,repo,content,status) values(?,?,?,?,?,?,?);"
        self.slcursor.execute(sql,(name,path,sha,html_url,repo,content,flag))
        return True
    
    '''
    获取扫描任务的扫描结果
    '''
    def selectallscanlist(self):
        sql = "select * from scanlist"
        self.slcursor.execute(sql)
        values = self.slcursor.fetchall()
        
        return values
    
    '''
    获取所有需要处理的扫描结果
    '''
    def selectscanlistBystatus(self,status):
        data=[]
        #r如果搜索待处理的结果，需要先获取status=1和status=2的数据
        if(status == '0'):
            #先获取二级搜索关键结果
            sql = "select * from scanlist where status = '1'"
            self.slcursor.execute(sql)
            values = self.slcursor.fetchall()
            for item in values:
                jsonitem={}
                jsonitem['id']=item[0]
                jsonitem['name']=item[1]
                jsonitem['path']=item[2]
                jsonitem['sha']=item[3]
                jsonitem['html_url']=item[4]
                jsonitem['reponame']=item[5]
                jsonitem['content']=item[6]
                jsonitem['disable']=False
                jsonitem['avatar']='/github.jpg'
                data.append(jsonitem)
            #在获取仓库搜索关键词
            sql = "select * from scanlist where status = '2'"
            self.slcursor.execute(sql)
            values = self.slcursor.fetchall()        
            for item in values:
                jsonitem={}
                jsonitem['id']=item[0]
                jsonitem['name']=item[1]
                jsonitem['path']=item[2]
                jsonitem['sha']=item[3]
                jsonitem['html_url']=item[4]
                jsonitem['reponame']=item[5]
                jsonitem['content']=item[6]
                jsonitem['disable']=False
                jsonitem['avatar']='/github.jpg'
                data.append(jsonitem)
        #根据status查询结果    
        sql = "select * from scanlist where status = ?"
        self.slcursor.execute(sql,[(status)])
        values = self.slcursor.fetchall()
        for item in values:
            jsonitem={}
            jsonitem['id']=item[0]
            jsonitem['name']=item[1]
            jsonitem['path']=item[2]
            jsonitem['sha']=item[3]
            jsonitem['html_url']=item[4]
            jsonitem['reponame']=item[5]
            jsonitem['content']=item[6]
            jsonitem['disable']=False
            jsonitem['avatar']='/github.jpg'
            data.append(jsonitem)
        
        return data
    
    def selectscanlist(self,sha):
        sql = "select * from scanlist where sha =?"
        self.slcursor.execute(sql,[(sha)])
        values = self.slcursor.fetchall()
        return values
    '''
    更新一条扫描结果的状态，是否屏蔽
    status:
        0:未处理
        3:误报
        4:已处理
    '''
    def updatescanlist(self,sha,status):
        sql = "update scanlist set status=? where sha=?"
        self.slcursor.execute(sql,(status,sha))
        return True
    
    def updatescanlistByid(self,id,status):
        sql = "update scanlist set status=? where id=?"
        self.slcursor.execute(sql,(status,id))
        return True
    
    '''
    更新所有未处理的条目为忽略
    '''
    def updateallignore(self,status):
        sql = "update scanlist set status=? where status=0"
        self.slcursor.execute(sql,(status))
        
        sql = "update scanlist set status=? where status=1"
        self.slcursor.execute(sql,(status))
         
        sql = "update scanlist set status=? where status=2"
        self.slcursor.execute(sql,(status))
        return True
        
    '''
    删除某条记录
    '''
    def deletescanlist(self,id):
        sql = "delete from scanlist where id =?"
        self.slcursor.execute(sql,[(id)])
        return True
    '''
    判断文件的MD5值是否已经存在
    '''
    def md5isExist(self,id,md5):
        self.openscanlist(id)
        sql = "select id from scanlist where sha = ?"
        self.slcursor.execute(sql,[(md5)])
        values = self.slcursor.fetchall()
        self.closescanlist()
        if len(values) != 0:
            return True
        else:
            return False
    
    
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
    
    