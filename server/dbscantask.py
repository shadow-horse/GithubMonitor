# -*- coding:utf-8 -*-

'''
操作scantask表
    1. 添加扫描任务
    2. 删除扫描任务
    3. 查询扫描任务
    4. 修改扫描任务
    5. 扫描任务状态
    
'''
import sqlite3
import json

class dbscantask:
    def __init__(self):
        self.maindb = 'main.db'
        self.scantask = 'scantask'
        self.current = 0
        self.pageSize = 0
    
    def getCurrent(self):
        return self.current
    def getPagesize(self):
        return self.pageSize
        
    #初始化一条记录
    def createdemodata(self):
        conn = sqlite3.connect(self.maindb)
        cursor = conn.cursor()
        sql = "insert into scantask ( name,f_keys,s_keys,repo_keys,parent_id,states) values ("\
            + "\'扫描任务\',"\
            + "\'test.com \',"\
            + "\'username password passwd\',"\
            + "\'password: passwd:\',"\
        + "\'0\',"\
        + "\'0\'"\
        + ")"
        cursor.execute(sql)
        cursor.close()
        conn.commit()
        conn.close()
     
    '''
    插入创建的扫描任务信息
    '''
    def insertscantask(self,name,f_keys,s_keys,repo_keys,parent_id=0,states=0):
        conn = sqlite3.connect(self.maindb)
        cursor = conn.cursor()
        sql = "insert into scantask ( name,f_keys,s_keys,repo_keys,parent_id,states) values (?,?,?,?,?,?)"
        cursor.execute(sql,(name,f_keys,s_keys,repo_keys,parent_id,states))
        sql = "select id from scantask where name = ? and f_keys = ? and s_keys=? and repo_keys=? and parent_id=? and states=?"
        cursor.execute(sql,(name,f_keys,s_keys,repo_keys,parent_id,states))
        value = cursor.fetchall()
        cursor.close()
        conn.commit()
        conn.close()
        return value[0]
    
    '''
    创建扫描任务存储DB    
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
    删除一条扫描记录
    '''
    def deletescanlist(self,id=None):
        if(id == None):
            return 
        conn = sqlite3.connect(self.maindb)
        cursor = conn.cursor()        
        sql = "delete from scantask where id =?"
        print(id)
        cursor.execute(sql,[(id)])
        cursor.close()
        conn.commit()
        conn.close()
        return 
    '''
    删除N条记录
    '''
    def removescanlist(self,keys=[]):
        for id in keys:
            self.deletescanlist(id)
        return 
    
    #查询扫描任务
    def queryscanlist(self,name):
        conn = sqlite3.connect(self.maindb)
        cursor = conn.cursor()
        sql = "select * from scantask where name like ?"
        name = '%'+name+'%'
        cursor.execute(sql,[(name)])
        values = cursor.fetchall()
        data = self.taskjsondata(values)
        cursor.close()
        conn.close()
        return data
    def queryscanlistByid(self,id):
        conn = sqlite3.connect(self.maindb)
        cursor = conn.cursor()
        sql = "select * from scantask where id = ?"
        cursor.execute(sql,[(id)])
        values = cursor.fetchall()
        cursor.close()
        conn.close()
        return values
    '''
    更新扫描任务状态
    states:
        0:未扫描
        1:扫描中
        2:扫描结束
    '''
    def uptaskstatusByid(self,id,states):
        conn = sqlite3.connect(self.maindb)
        cursor = conn.cursor()
        sql = "update scantask set states=? where id=?"
        cursor.execute(sql,(states,id))
        cursor.close()
        conn.commit()
        conn.close()
        return True
    
    #获取扫描任务
    def getscanlist(self,current='1',pageSize='10',sorter='',name=None,f_keys=None,s_keys=None,repo_keys=None,parent_id=None):
        conn = sqlite3.connect(self.maindb)
        cursor = conn.cursor()
        current = int(current)
        pageSize = int(pageSize)
        self.current = current
        self.pageSize = pageSize
        offset = pageSize * (current -1)
        sql = "select * from scantask "
        if(name !=None or f_keys!=None or s_keys!=None):
            sql = sql + " where "
        if (name !=None):
            sql = sql + "name like '%"+name+"%' "
        if (f_keys != None):
            sql = sql + " f_keys like '%"+f_keys+"%' "
        if(s_keys !=None):
            sql = sql + " s_keys like '%"+s_keys+"%' "
        sql = sql + " limit ? offset ?"
        cursor.execute(sql,(pageSize,offset))
        values = cursor.fetchall()
        data = self.taskjsondata(values)
        cursor.close()
        conn.close()
        return data
    
    def getscanlistnums(self):
        conn = sqlite3.connect(self.maindb)
        cursor = conn.cursor()
        sql = "select count(id) from scantask"
        cursor.execute(sql)
        values = cursor.fetchall()
        cursor.close()
        conn.close()
        return values[0]  
       
    #json格式转换
    def taskjsondata(self,values):
        jsondata = []
        if(len(values) > 0):
            for value in values:
                itemjson = {}
                itemjson['id'] = value[0]
                itemjson['name'] = value[1]
                itemjson['f_keys']= value[2]
                itemjson['s_keys']= value[3]
                itemjson['repo_keys']= value[4]
                itemjson['parent_id']= value[5]
                if (value[6] == '0'):
                    itemjson['states']= '待扫描'
                elif (value[6] == '1'):
                    itemjson['states']= '扫描中'
                elif (value[6] == '2'):
                    itemjson['states']= '扫描结束'
                elif (value[6] == '3'):
                    itemjson['states']= '异常结束'
                jsondata.append(itemjson)
                
        return jsondata
        
     
if __name__=='__main__':
    scantask = dbscantask()
#     scantask.queryscanlist('扫描')
#     scantask.getscanlist(current='1', pageSize='10')
#     scantask.getscanlistnums()
    scantask.uptaskstatusByid(3,3)