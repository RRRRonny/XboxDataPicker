# version 1.0
# 将包含 api 信息的 csv 文件转换成 可识别的 ini 配置文件,csv 文件中必须包含 name 列,name 列的值将作为[section] 的值
# tips
# 1. 注意文件路径
# 2. 生成的 ini 文件包含 csv 第一行的信息,并且忽略第一列
#
# todo
# 1. 忽略字典中 name 字段
import argparse
import configparser

if __name__ == "__main__":
    conf = configparser.ConfigParser()
    parser = argparse.ArgumentParser("convert csv file to ini file")
    parser.add_argument("csv")
    parser.add_argument("ini")
    args = parser.parse_args()
    
    csv_path = args.csv
    ini_path = args.ini

    keys = []
    
    with open(csv_path,'rt') as f:
        line = f.readline()
        keys = line.split(',')[1:]
        max_len = len(keys)
        while line:
            arr = line.split(',',max_len)[1:]
            t_dict = {}
            t_len = len(arr)
            step = 0
            while step < t_len:
                t_dict[keys[step]] = arr[step]
                step += 1
            print("generate dict : {}".format(t_dict))
            conf[t_dict['name']] = t_dict
            line = f.readline()

    with open(ini_path,'w') as f:
        conf.write(f)