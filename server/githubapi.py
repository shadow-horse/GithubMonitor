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
        try:
            print('search code please wait 2 second......')
            self.session = requests.session()
            self.session.keep_alive = False
            time.sleep(1)
            url = 'https://api.github.com/search/code?q='+urllib.parse.quote(id)+'&sort=indexed&order=desc'
            url = '%s&page=%s&per_page=%s' %(url,page,per_page)
            result = self.session.get(url=url,headers=self.headers,timeout=10)
            if(not self.checkratelimit(result.headers)):
                return self.searchcode(id, page, per_page)
            self.session.close()
            if 'items' in result.json().keys():
                return result.json()
            else:
                return False
        except Exception as e:
            print('searchcode exception %s......' % (e))
            self.session.close()
            return False
    
    def searchrepositories(self,id):
        url = 'https://api.github.com/search/repositories?q='+urllib.parse.quote(id)
        self.session = requests.session()
        self.session.keep_alive = False
        result = self.session.get(url=url,headers=self.headers)
        self.session.close()
        return result.json()
    
    def searchcommits(self,id):
        url = 'https://api.github.com/search/commits?q='+urllib.parse.quote(id)
        self.session = requests.session()
        self.session.keep_alive = False        
        result = self.session.get(url=url,headers=self.headers)
        self.session.close()
        return result.json()
    
    def searchissues(self,id):
        url = 'https://api.github.com/search/issues?q='+urllib.parse.quote(id)
        self.session = requests.session()
        self.session.keep_alive = False 
        result = self.session.get(url=url,headers=self.headers)
        self.session.close()
        return result.json() 
    
    
    def searchrawfile(self,url):
        #正则替换 github.com => raw.githubusercontent.com 
        rawurl = url.replace('github.com','raw.githubusercontent.com',1).replace('/blob/','/',1)
        time.sleep(2)
        ses = requests.session()
        #关闭多余连接，解决Max retries exceeded with url问题
        ses.keep_alive = False
        text=''
        try:
            result = ses.get(rawurl)
            self.checkratelimit(result.headers)
            text = result.text
        except Exception as e:
            print('searchrawfile exception %s......' % (e))
            #如果获取源文件失败，则返回以下内容，默认记录到扫描结果中，以便操作人去访问连接并检查
            text = 'Get raw file failed, please access the link.'
        ses.close()
        return text
    
    def searchfilename(self,repo,name,path,id):
        #通过API接口搜索具体的文件，具体的path，具体的仓库
        path = path[:path.rfind('/')]
        url = 'https://api.github.com/search/code?q='+urllib.parse.quote(id)+ ' path:' +path+ ' filename:'+name +' repo:'+repo + '&sort=indexed&order=desc'
        self.session = requests.session()
        self.session.keep_alive = False 
        try:
            result = self.session.get(url=url,headers=self.headers)
            if(not self.checkratelimit(result.headers)):
                return self.searchfilename(repo, name, path,id)
            
            self.session.close()
            if 'items' in result.json().keys():
                return result.json()
            else:
                return False
        
        except Exception as e:
            print('searchfilename exception %s......' % (e))
            self.session.close()
            return False
    
    def getkeywords(self,html_url,id):
        #确定该文件需要展示时，调用该方法获取存在搜索关键词的代码片段，发现代码片段后，取前一行和后一行进行拼接
        rawcontent = self.searchrawfile(html_url)
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
            result = rawcontent
#         print(result)
        return result
    
    def close(self):
        self.session.close()
    
    def checkratelimit(self,headers):
        if 'X-RateLimit-Remaining' in headers.keys():
            remaining = headers['X-RateLimit-Remaining']
            if remaining == '1':
                print('ratelimit please wait 60 seconds......')
                time.sleep(30)
                return True
            
        if 'Retry-After' in headers.keys():
            retry_after = headers['Retry-After']
            print('Retry-After please wait %s seconds......' % (retry_after))
            time.sleep(int(retry_after))
            return False
        return True
    
    
if __name__ == '__main__':
    api = githubapi()
    
#     res = api.searchcode('hello.com.cn')
#     total_count = res['total_count']
#     pages = math.floor(total_count/100)
#     print(pages)
#     items = res['items']
#     ii = 0
#     for i in items:
#         ii = ii+1
#         print(ii)
#         print(i['name'])
#         print(i['path'])
#         print(i['sha'])
#         print(i['html_url'])
#         print(i['repository']['full_name'])
#     time.sleep(2)
#     print('===========================')
#     for i in range(2,pages+1):
#         res = api.searchcode('vivo.com.cn',i)
#         items = res['items']
#         for i in items:
#             print(i['name'])
#         break
#     time.sleep(2)
#     print("===========================")
    res = api.getkeywords('https://github.com/starnightcyber/subDomains/blob/b340e23eee2c0fa9332256a2c458f3d53a3f3962/vivo.com.cn/vivo.com.cn-subdomain.txt', 'vivo.com.cn')
    print(res)
#     time.sleep(5)
#     res = api.searchfilename('Even521/spring-boot-sample', 't_company.sql', 'spring-boot-demo/spring-boot-quartz/src/main/resources/db/t_company.sql','维沃移动')
#     print(res)
   