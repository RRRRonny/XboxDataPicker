'''
为主程序提供数据支持
'''
import sqlite3
import configparser
import requests
import re
import os
import json

from . import api_supporter 

'''
连接件
'''
class DataProvider:
    database = "test.db"
    api_key = "apikey"

    def __init__(self,config_file,database = "test.db"):
        self.database = database
        cparser = configparser.ConfigParser()
        cparser.read(config_file)
        self.api_key = cparser['default']['apikey']

        # init the DataBaseHelper and NetworkRequester
        self.data_helper = DataBaseHelper()
        self.request_helper = NetworkRequester(self.api_key)


    def get_xuid(self,gametag):
        # 从数据库查询
        result = self.data_helper.get_xuid(gametag)
        if  result['isSuccess'] :
            print("read xuid data from local database")
            return result['content']
        else:
            print("loacl databse has no xuid data")
            # 从 api 拉取
            r = self.request_helper.request("Gamertag XUID",gamertag = gametag)
            if r.status_code == 200:
                # 写入数据库
                self.data_helper.insert_gamertag_and_xuid(gametag,r.text)
                return r.text
            else:
                return "didn't get the xuid form xboxapi.com , the result is {}".format(r.text)


    def get_gametag(self,xuid):
        return "gametag"

    def get_player_onegames(self,xuid):
        result = self.data_helper.get_own_one_games(xuid)
        print_list = []
        if  result['isSuccess'] :
            print("read xbox one games data from local database")
            # 返回拥有的 title id
            title_list = result['content']
            # 循环查询游戏具体信息
            for title in title_list:
                detail = self.data_helper.get_one_game_detail(title[0])
                if detail['isSuccess']:
                    print_list.append(detail['content'])
                else:
                    # 如果没有查询到,说明数据库内有脏数据
                    print_list.append("dirty data in database")
        else:
            print("loacl databse has no xbox one games data")
            r = self.request_helper.request("Xbox ONE Games",xuid = xuid)
            if r.status_code == 200:
                # 写入数据库
                json_str = r.text
                json_data = json.loads(json_str)
                title_list = json_data['titles']
                for title in title_list:
                    # 根据 json 生成 print list
                    print_list.append({
                        'name' : title['name'],
                        'titleId' : title['titleId'],
                        'titleType' : title['titleType'],
                        'platform' : title['platform'],
                        'maxGamerscore' : title['maxGamerscore']
                    })
                    # 写入 own 
                    self.data_helper.insert_own(xuid,title['titleId'])
                    # 写入 detail
                    # 查询该游戏是否存在
                    if not self.data_helper.get_one_game_detail(title['titleId'])['isSuccess']:
                        self.data_helper.insert_game_detail(title['name'],title['titleId'],title['titleType'],title['platform'],title['maxGamerscore'])
            else:
                print_list.append("didn't get the xuid form xboxapi.com , the result is {}".format(r.text))
        return print_list

    def get_player_360games(self,xuid):
        return "360 games"
    
    def get_player_achievements(self,xuid,achievement_id):
        pass

    def get_player_profile(self,xuid):
        pass

    def get_player_gamecard(self,xuid):
        pass

    def get_palyer_game_stats(self,xuid):
        pass
    
    def get_player_singal_game_stat(self,xuid,titleid):
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
        response = requests.get(url,headers = self.request_header)

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
    database = "default.db"

    def __init__(self,database = "default.db"):
        self.database = os.path.abspath('.') + '/data/' + database
        print("debug: database is {}".format(self.database))
        self.__check_table_stat()


    def get_xuid(self,gamertag):
        sql = 'select xuid from gamer_info where gamertag = ?'
        result = self.execute_sql(sql,gamertag)
        if len(result['result_list']) > 0:
            return {
                'isSuccess' : True,
                'content' : result['result_list'][0][0]
            }
        else:
            return{
                'isSuccess' : False,
                'content' : None
            }

    def get_own_one_games(self,xuid):
        sql = 'SELECT title_id FROM gamer_own_game where xuid = ?'
        result = self.execute_sql(sql,xuid)
        print("debug : own one games select result , the result list is {}".format(result['result_list']))
        if len(result['result_list']) > 0:
            return {
                'isSuccess' : True,
                'content' : result['result_list']
            }
        else:
            return{
                'isSuccess' : False,
                'content' : None
            }
    
    def get_one_game_detail(self,title_id):
        sql = 'select name,title_id,titleType,maxGamerscore from games where title_id = ?'
        result = self.execute_sql(sql,title_id)
        if len(result['result_list']) > 0:
            return {
                'isSuccess' : True,
                'content' : result['result_list']
            }
        else:
            return{
                'isSuccess' : False,
                'content' : None
            }

    def insert_own(self,xuid,title_id):
        sql = "insert into gamer_own_game(xuid,title_id) VALUES (?,?)"
        result = self.execute_sql(sql,xuid,title_id)
        return result['count']
    
    def insert_game_detail(self,name,title_id,title_type,platform,score):
        sql = "insert  into games(name, title_id, titleType, platform, maxGamerscore) values (?,?,?,?,?)"
        result = self.execute_sql(sql,name,title_id,title_type,platform,score)
        return result['count']

    def insert_gamertag_and_xuid(self,gamertag,xuid):
        sql = "insert into gamer_info(gamertag,xuid) values (?,?)"
        result = self.execute_sql(sql,gamertag,xuid)
        return result['count']

    def get_gametag(self,xuid):
        pass

    def execute_sql(self,sql,*values):
        # print("the vaules is {}".format(values))
        cursor =  self.__get_conn().cursor()
        cursor.execute(sql,values)
        # cursor.execute("select xuid from gamer_info where gamertag = 'SevenFii'")
        count = cursor.rowcount
        result_list = cursor.fetchall()
        cursor.close()
        self.conn.commit()
        self.__close_conn()
        # print("count is {}".format(count))
        # print("result is {}".format(result_list))
        return {
            'count' : count,
            'result_list' : result_list
        }


    # pirvate functions
    def __get_conn(self):
        self.conn = sqlite3.connect(self.database)
        return self.conn
    
    def __close_conn(self):
        self.conn.close()

    
    def __check_table_stat(self):
        conf = configparser.ConfigParser()
        current_path = os.path.abspath('.')
        conf_path = current_path + '/config/app.config.ini'
        conf.read(conf_path)
        # print("config file path is {}".format(conf_path))
        if not conf['database'].getboolean('table_created'):
            # 未创建表
            self.__create_all_tables()
            conf['database']['table_created'] = 'True'
            with open(conf_path,'w') as f:
                conf.write(f)

    def __create_all_tables(self):
        self.__create_gamer_table()
        self.__create_games_games()
        self.__create_gamer_own_game()
    


    def __create_gamer_table(self):
        cursor =  self.__get_conn().cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS gamer_info(
				id integer PRIMARY KEY AUTOINCREMENT,
				gamertag text NOT NULL,
				xuid text NOT NULL,
				onegame_count integer,
				threegame_count integer,
				achievement_point integer)''')
        cursor.close()
        self.__close_conn()

    def __create_games_games(self):
        cursor =  self.__get_conn().cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS games(
            id integer PRIMARY KEY AUTOINCREMENT,
            name text NOT NULL,
            title_id text NOT NULL,
            titleType text NOT NULL,
            platform text NOT NULL,
            maxGamerscore integer NOT NULL)''')
        cursor.close()
        self.__close_conn()

    def __create_gamer_own_game(self):
        cursor =  self.__get_conn().cursor()
        cursor.execute('''create table IF NOT EXISTS gamer_own_game(
            id integer primary key autoincrement,
            xuid text not null,
            title_id text not null)''')
        cursor.close()
        self.__close_conn()