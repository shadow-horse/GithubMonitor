# -*- coding:utf-8 -*-

'''
创建存储DB
'''
import sqlite3

'''
创建根数据库，用于保存创建的扫描任务
扫描任务：
    任务id
    任务名称
    搜索code一级关键字
    搜索code二级关键字 （基于一级结果进行搜索）
    搜索该repo二级关键字 （基于一级结果搜索对应的repo中二级关键词）
    父任务id (可通过选择父任务id的方式，基于父任务的扫描结果进行搜索)
    扫描状态
    
    
'''
def createmaindbsql():
    #连接到数据库
    #数据库文件是“main.db”
    #如果数据库不存在的话，将会自动创建一个 数据库
    conn = sqlite3.connect("main.db")
    
    #创建一个游标
    cursor = conn.cursor()
    
    #执行一条语句,创建扫描任务表 scantask
    sql = "create table if not exists scantask ("\
        + "id integer primary key autoincrement," \
        + "name varchar(30), " \
        + "f_keys varchar(256),"\
        + "s_keys varchar(256),"\
        + "repo_keys varchar(256),"\
        + "parent_id varchar(20),"\
        + "states varchar(20)"\
        + ")"
    print(sql)
    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()
#删除扫描任务表
def deletescantasktable():
    conn = sqlite3.connect("main.db")
     #创建一个游标
    cursor = conn.cursor()
    sql ="drop table scantask"
    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()
 
     

    
if __name__ == '__main__':
    createmaindbsql()