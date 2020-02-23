# -*- coding:utf-8 -*-
'''
读完配置文件
'''
import os
import configparser

class config:
    def __init__(self):
        # 项目路径
        self.rootDir = os.path.split(os.path.realpath(__file__))[0]
        # config.ini文件路径
        self.configFilePath = os.path.join(self.rootDir, 'config.ini') 
    def get_config_values(self,section, option):
        """
        根据传入的section获取对应的value
        :param section: ini配置文件中用[]标识的内容
        :return:
        """
        con = configparser.ConfigParser()
        con.read(self.configFilePath)
        # return config.items(section=section)
        return con.get(section=section, option=option)
 
 
if __name__ == '__main__':
    cof = config()
    result = cof.get_config_values('GITHUB', 'AUTH_TOKEN')
    print(result)