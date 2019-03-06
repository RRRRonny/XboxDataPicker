'''
为主程序提供数据支持
'''
import sqlite3
import configparser
import requests
import re

from . import api_supporter 

'''
连接件
'''
class DataProvider:
    database = "test.db"
    api_key = "apikey"

    def __init__(self,database,config_file):
        self.database = database
        cparser = configparser.ConfigParser()
        cparser.read(config_file)
        self.api_key = cparser['default']['apikey']
        # init the DataBaseHelper and NetworkRequester
        self.data_helper = DataBaseHelper(self.database)
        self.request_helper = NetworkRequester(self.api_key)


    def get_xuid(self,gametag):
        return "xuid"
    
    def get_gametag(self,xuid):
        return "gametag"

    def get_player_onegames(self,xuid):
        return "xboxonegames"

    def get_player_360games(self,xuid):
        return "360 games"
    
    def get_player_achievements(self,xuid,achievement_id):
        pass

    def get_player_status(self,xuid):
        pass
'''
网络请求
todo
1. 分组 api 和 api key
'''
class NetworkRequester:
    def __init__(self,apikey):
        self.apikey = apikey  
        # init the api supporter
        self.supporter = api_supporter.ApiSupporter()
        self.__generate_header()
        self.url = 'ip.gs'

    def __generate_header(self):
        self.request_header =  {'X-AUTH': self.apikey}

    # 有了 api supporter 之后,应该直接使用 api 名发起请求,否则分层就没有意义
    '''
    请求 /v2/{xuid}/profile 时,
    需要传入 xuid = "abc" . 函数会自动将{xuid}替换成 abc
    '''
    def request(self,api_name,**values):
        url = self.supporter.get_api_url(api_name)
        url = self.replace(values,url)
        response = requests.get(url,self.request_header)
        return response

    def replace(self,value_dict,origin_str):
        keys = value_dict.keys()
        key_list = list(keys)
        for key in key_list:
            pattern = '\\{' + key + '\\}'
            origin_str = re.sub(pattern,value_dict[key],origin_str)
        return origin_str


'''
数据据查询
'''
class DataBaseHelper:
    database = "test.db"


    def __init__(self,database):
        self.database = database
    
    def create_table(self,sql):
        pass

    def delete_table(self,table_nmame):
        pass

    def execute_sql(self,sql):
        cursor = self.get_conn().cursor()
        cursor.execute(sql)
        cursor.close()
        self.close_conn()
        
    def get_conn(self):
        self.conn = sqlite3.connect(self.database)
        return self.conn
    
    def close_conn(self):
        self.conn.close()






