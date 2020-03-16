# -*- coding:utf-8 -*-
'''
封装http请求
'''
import config
import requests
import urllib.parse
import time
import math
from asyncio.tasks import sleep
requests.adapters.DEFAULT_RETRIES = 5

class githubapi:
    def __init__(self):
        cof = config.config()
        self.auth_token = 'token ' + cof.get_config_values('GITHUB', 'AUTH_TOKEN')
        self.headers = {'Authorization':self.auth_token,'Connection':'close','User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'}
        
    def searchcode(self,id,page=1,per_page=100):
        redata = ''
        session = requests.session()
        session.keep_alive = False
        try:
            print('search code please wait 2 second......')
            time.sleep(2)
            url = 'https://api.github.com/search/code?q='+urllib.parse.quote(id)+'&sort=indexed&order=desc'
            url = '%s&page=%s&per_page=%s' %(url,page,per_page)
            result = session.get(url=url,headers=self.headers,timeout=60)
            #循环检查是否被Github限制，如股限制则重新进行请求
            if(self.checkratelimit(result.headers)):
                session.close()
                redata =  self.searchcode(id, page, per_page)
            else:
                if 'items' in result.json().keys():
                    redata =  result.json()
                else:
                    print('searchcode items not in result.json.keys()......')
                    redata =  False
        except Exception as e:
            print('searchcode exception %s......' % (e))
            redata =  False
        
        session.close()
        return redata
            
    
    def searchrepositories(self,id):
        url = 'https://api.github.com/search/repositories?q='+urllib.parse.quote(id)
        session = requests.session()
        session.keep_alive = False
        result = session.get(url=url,headers=self.headers)
        session.close()
        return result.json()
    
    def searchcommits(self,id):
        url = 'https://api.github.com/search/commits?q='+urllib.parse.quote(id)
        session = requests.session()
#         session.keep_alive = False        
        result = session.get(url=url,headers=self.headers)
        session.close()
        return result.json()
    
    def searchissues(self,id):
        url = 'https://api.github.com/search/issues?q='+urllib.parse.quote(id)
        session = requests.session()
#         session.keep_alive = False 
        result = session.get(url=url,headers=self.headers)
        session.close()
        return result.json() 
    
    

    
    def searchfilename(self,repo,name,path,id):
        #通过API接口搜索具体的文件，具体的path，具体的仓库
        resdata = ''
        path = path[:path.rfind('/')]
        url = 'https://api.github.com/search/code?q='+urllib.parse.quote(id)+ '+path:' +path+ '+filename:'+name +'+repo:'+repo + '&sort=indexed&order=desc'
        session = requests.session()
        session.keep_alive = False 
        try:
            result = session.get(url=url,headers=self.headers)
            if(self.checkratelimit(result.headers)):
                session.close()
                return self.searchfilename(repo, name, path,id)
            
            if 'items' in result.json().keys():
                if result.json()['total_count'] > 0 :
                    resdata = True
                else:
                    resdata =  False
            else:
                print('searchfilename items not in result.json().keys.')
                resdata =  True  #如果异常或访问失败，默认记录
        
        except Exception as e:
            print('searchfilename exception %s......' % (e))
            resdata = True      #如果异常或访问失败，默认记录
        session.close()
        return resdata
        
    #在仓库中搜索关键词
    def searchByrepo(self,repo,id):
        resdata = ''
        url = 'https://api.github.com/search/code?q='+urllib.parse.quote(id)+ '+repo:'+repo + '&sort=indexed&order=desc'
        session = requests.session()
        session.keep_alive = False 
        try:
            result = session.get(url=url,headers=self.headers)
            if(self.checkratelimit(result.headers)):
                session.close()
                resdata = self.searchByrepo(repo,id)
            else:
                if 'items' in result.json().keys():
                    resdata =  result.json()
                else:
                    print('searchByrepo items not in result.json().keys')
                    resdata =  False
        
        except Exception as e:
            print('searchByrepo exception %s......' % (e))
            resdata =  False
        
        session.close()
        return resdata
    
    def getkeywords(self,html_url,id):
        #确定该文件需要展示时，调用该方法获取存在搜索关键词的代码片段，发现代码片段后，取前一行和后一行进行拼接
        rawcontent = self.searchrawfile(html_url)
        if(not rawcontent):
            result = 'Get rawfile failed. Please click the link.'
            return result
        
        content = rawcontent.split('\n')
        #返回查询结果，如果查询结果超过5个，则终止，以免内容过多
        result = ''
        resultindex = 1
        index = 0
        for line in content:
            index = index + 1
            if(id in line):
                if(resultindex > 5):
                    break;
                resultindex = resultindex+1
                result = result + '%s:%s\n\n' %(index,line)
        #如果result为空，意味着没有搜索到关键词，但是应该能搜索到，故设置result=content
        if result == '':
            result = 'file search content is null.'
        return result

    def searchrawfile(self,url):
        #正则替换 github.com => raw.githubusercontent.com 
        rawurl = url.replace('github.com','raw.githubusercontent.com',1).replace('/blob/','/',1)
        time.sleep(2)
        ses = requests.session()
        #关闭多余连接，解决Max retries exceeded with url问题
        ses.keep_alive = False
        text=''
        try:
            result = ses.get(rawurl,timeout = 30)
            print(result.headers)
#             self.checkratelimit(result.headers)
            text = result.text
        except Exception as e:
            print('searchrawfile exception %s......' % (e))
            #如果获取源文件失败，则返回以下内容，默认记录到扫描结果中，以便操作人去访问连接并检查
            text = False
        ses.close()
        return text
    
    
    def checkratelimit(self,headers):
        if 'X-RateLimit-Remaining' in headers.keys():
            remaining = headers['X-RateLimit-Remaining']
            if remaining == '1':
                print('ratelimit=1 please wait 30 seconds......')
                time.sleep(30)
                return True
            if remaining == '0':
                print('ratelimit=0 please wait 10 seconds......')
                time.sleep(10)
                return True
            
        if 'Retry-After' in headers.keys():
            retry_after = headers['Retry-After']
            print('Retry-After please wait %s seconds......' % (retry_after))
            time.sleep(int(retry_after))
            return True
        if 'Status' in headers.keys():
            if(headers['Status'] == '403 Forbidden'):
                time.sleep(10)
                return True
        return False
    
    
if __name__ == '__main__':
    api = githubapi()
    
    res = api.searchcode('helloworld')
    total_count = res['total_count']
    pages = math.floor(total_count/100) + 1
    print(pages)
    pages = 3
    items = res['items']
#     print(res)
    ii = 0
    for i in items:
        ii = ii+1
        print(i['name'])
#         print(i['path'])
#         print(i['sha'])
#         print(i['html_url'])
#         print(i['repository']['full_name'])
        
#     res = api.searchByrepo('Mynameisfwk', 'liugaoren')
#     print(res)
#     time.sleep(2)
#     print('===========================')
    for i in range(2,pages+1):
        print('-----------------------------------')
        res = api.searchcode('helloworld',page = i)
        items = res['items']
        for j in items:
            ii = ii+1
            print(j['name'])
        

#     time.sleep(2)
#     print("===========================")
#     res = api.getkeywords('https://github.com/starnightcyber/subDomains/blob/b340e23eee2c0fa9332256a2c458f3d53a3f3962/test.com.cn/test.com.cn-subdomain.txt', 'test.com.cn')
#     print(res)
#     time.sleep(5)
#     res = api.searchfilename('Even521/spring-boot-sample', 't_company.sql', 'spring-boot-demo/spring-boot-quartz/src/main/resources/db/t_company.sql','liuyifeng')
#     print(res)
   