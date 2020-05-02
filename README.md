## GithubMonitor

### 前言

Github代码监控程序很多，如Github-Monitor，但是无法满足灵活的search规则，会存在比较多的误报，故重新写个Github代码监控程序，当然不一定比已有的完美，主要是借此机会锻炼下代码开发能力，学习前端开发框架ant design pro，能够快速的搭建简单的应用程序。    


### 功能
1）创建扫描任务，管理任务    
2）查看任务扫描结果  
3）标记扫描结果：忽略  
4）扫描逻辑：
		
	1. 一级关键词: 支持Github api v3搜索格式search code 
	2. 二级关键词: 以|符号分割，会分别在一级关键词搜索的页面继续扫描分割的字符串   
	3. 仓库关键词：以|符号分割，会在一级关键词搜索的仓库中继续搜索分割的字符  
	4. 设置定时扫描任务 
	5. 基于扫描结果的二次扫描（未实现）
	6. 修改已有的扫描任务
	7. 实现针对不同文件类型的过滤，有限针对某些文件类型告警  
	8. 代码监控主要用于监控新增的代码，随时检查是否存在泄漏
#### 修改记录
1. 在实际操作中，忽略误报是比较常见的操作，仅仅以单个文件忽略是不行的，需要增忽略仓库的功能 【2020/5/2】  
2. 监控更多的目的是监控新增的和公司相关的代码，针对已经出现过的文件，如果确定这个仓库和公司无关，可以比较为永久忽略：文件永久忽略/仓库永久忽略，目前是如果文件hash发生变化，则会重新告警，导致告警数量偏多  
3. 


### 1. Github REST API 问题 

1. Github api存在速率限制  

	Github api在访问时存在速率限制，可参考API说明文档，在使用时需要判断响应头'Retry-After',下次请求需要等待的时间。  
	
		if 'Retry-After' in headers.keys():
            retry_after = headers['Retry-After']
            print('Retry-After please wait %s seconds......' % (retry_after))
            time.sleep(int(retry_after))
            
2. 在循环调用时，在跑到第9页时会抛出异常 'Max retries exceeded with url'

		按照网上说明，配置了header{'Connection':'close'},并使用session，搜索完成后关闭该session。  

3. Github API searchcode返回的结果不超过1000条  
	
	最初时不清楚API的返回结果限制，处理异常报错，经查看API发现是code搜索存在1000条的限制. 
	
		1. search code搜索默认设置搜索条件sort=indexed&order=desc，获取前1000条搜索数据。  
		2. 为了解决1000条的限制，可以通过条件搜索repo，例如限制创建的时间，在从repo中进行code搜索：https://api.github.com/search/repositories?q=language:Java&created>=2013-04-11T00:00:00Z&sort=created&order=asc
		
4. Failed to establish a new connection: [Errno 60] Operation timed out'))

		在本地跑脚本时经常遇到超时的情况，很不稳定，在云主机上则没有问题，暂时未解决，可能是本地网络问题。  
	
5. 铜鼓API接口扫描，如何获取对应的代码片段（暂未解决）


### 2. Client前台

基于Ant Design Pro 4.0搭建，教程：https://pro.ant.design/docs/upgrade-v4-cn    
Ant Design组件：https://ant.design/docs/react/introduce-cn   

环境搭建：

	1. 安装npm: yum install npm 
	2. 安装国内npm源cnpm: npm install -g cnpm --registry=https://registry.npm.taobao.org
	3. cnpm install
运行前台:

	1. npm run start (如果运行报错，请升级Nodejs和npm版本)
	2. 后台运行命令，执行完成后，以exit退出会话： nohup npm run start > msg.out &

### 3. Server服务端

Python配置环境依赖：  

	1. pip3 install pydantic
	2. pip3 install fastapi
	3. pip3 install uvicorn

1. config.ini 配置github token  

		###配置github认证token
		[GITHUB]
		AUTH_TOKEN=
2. 初始化数据库

 		python3 dbinstall.py 
 		
3. 启动服务端

 		python3 serverstart.py 
4. 启动定时监控  

		python3 timingtask.py


### 4. 效果图 

1. 访问任务列表：http://127.0.0.1:8000/welcome
	![](https://github.com/shadow-horse/GithubMonitor/blob/master/img/tasklist.png)
2. 访问任务的扫描结果
	![](https://github.com/shadow-horse/GithubMonitor/blob/master/img/scanlist.png)


