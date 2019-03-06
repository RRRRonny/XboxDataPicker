'''
todo
1. 增加本地数据库支持
2. 增加懒惰模式,-l 该模式下静默优先使用本地数据,本地没有数据时才会请求
3. 增加本地模式,-L 该模式只会调用本地数据
4. 更新本地数据库 
    4.1 update database :更新整个数据库
    4.2 update {gametag/xuid} :更新指定的用户数据到本地,如果本地没有数据则增加该条数据
    4.3 update -i inputfile.txt :使用配置文件更新指定的用户集
5. 日志支持
6. 保留本地原始文件
7. clear 命令, 清除本地多余文件
8. 从外部文件读取 api @done
'''

import argparse
import requests
import configparser
import re
import json
import os
import sqlite3

# custom moudle
import core.data_provider as dp
import core.api_supporter as api_supporter

# request header use in request function
headers = {}

# config setting
conf = configparser.ConfigParser()
conf_api = configparser.ConfigParser()

# files path
current_path = os.path.abspath('.')
data_path = current_path + "/data"
config_path = current_path + "/config"
log_path = current_path + "/log"

# api url
api_urls = {}

# constant
LOG_NAME = "/app.log"
#todo
CONFIG_NAME =config_path + "/app.config.ini"
CONFIG_API_NAME = config_path + "/api.url.ini"


def load_config():
    global conf
    conf.read(CONFIG_NAME)
    apikey = conf['default']['apikey']
    global headers
    headers = {'X-AUTH': apikey}



def search(gametag):
    provider = dp.DataProvider(CONFIG_NAME)
    xuid = provider.get_xuid(gametag)
    print(xuid)


def info(gametag):
    provider = dp.DataProvider(CONFIG_NAME)
    xuid = provider.get_xuid(gametag)
    result = provider.get_player_onegames(xuid)
    print(result)


def download(gametag):
    print("download : now unavailable")


def mfilter(filter):
    print("filter : now unavailbale")


def test(message):
    print("execute func : test")
    # test the sqlite
    if message == 'db':
        conn = sqlite3.connect('data/default.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE COMPANY
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       AGE            INT     NOT NULL,
       ADDRESS        CHAR(50),
       SALARY         REAL);''')
        conn.commit()
        conn.close()
    




    elif message == 'json':
        datafile = 'data/1551625760_SevenFii_2535421044468041.json'
        with open(datafile,'r') as f:
            json_data = json.load(f)
            # dict_data = json.loads(json_data)
            titles = json_data['titles']
            for title in titles:
                print(title['name'])
    elif message == 'info':
        print("show debug info")
        print("python file itself's absoulte path is {}".format(current_path))
    elif message == 'api':
        supporter = api_supporter.ApiSupporter(CONFIG_API_NAME)
        print("get the api url \"Account XUID\" : {}".format(supporter.get_api_url("Account XUID")))



# command filter
command_filter = {
    'search': search,
    'info': info,
    'download': download,
    'filter' : mfilter,
    'test': test
}


def get_xuid(gametag):
    request_url = "https://xboxapi.com/v2/xuid/{gametag}"
    request_url = re.sub(r'\{gametag\}', gametag, request_url)
    global headers
    r = requests.get(request_url, headers=headers)
    return r.text


def get_xboxone_games(xuid, storefile=True):
    request_url = "https://xboxapi.com//v2/{xuid}/xboxonegames"
    request_url = re.sub(r'\{xuid\}', xuid, request_url)
    global headers
    r = requests.get(request_url, headers=headers)
    return r.text






def mian():
    # load config first
    load_config()

    base_commands = ['search', 'info', 'download', 'test']
    parser = argparse.ArgumentParser(description='Xbox Data Picker')
    parser.add_argument("command", help="the operation",
                        type=str, choices=base_commands,)
    parser.add_argument("value", help="")
    args = parser.parse_args()
    command = args.command
    value = args.value

    # debug
    # print("get the input values, command is {} , value is {}".format(command, value))

    command_func = command_filter[command]
    command_func(value)


if __name__ == "__main__":
    mian()
