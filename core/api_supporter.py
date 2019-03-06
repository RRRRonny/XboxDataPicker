'''
api supporter

todo
1. 增加文件是否存在的检测支持
'''
import configparser
import os 

class ApiSupporter:
    api_urls = {}

    '''
    conf_file 可以缺省,缺省情况下直接使用 config 下的 api.url.ini 文件
    '''
    def __init__(self,conf_file = "default"):
        if conf_file == "default":
            #print("use default config file")
            self.conf_file = os.path.abspath('.') + '/config' + '/api.url.ini'
        else:
            #print("use custom config file")
            self.conf_file = conf_file
        #print(self.conf_file)
        self.configparser = configparser.ConfigParser()
        self.__load_api_url()



    def get_api_url(self,api_name):
        base_url = self.api_urls['base']['url']
        specific_url = self.api_urls[api_name]['url']
        return base_url + specific_url
        

    def get_api_dict(self):
        return self.api_urls

    '''
    refresh the api dict from config file
    '''
    def refresh(self):
        self.__load_api_url()

    def __load_api_url(self):
        self.configparser.read(self.conf_file)
        sections = self.configparser.sections()
        for section in sections:
            options = self.configparser.options(section)
            self.api_urls[section] = {}
            for option in options:
                self.api_urls[section][option] = self.configparser[section][option]
    

   