#!/bin/zsh
# this is the script base on xboxapi.com .which can check specified player public data simply
# 
# @author:RNTio
#
# version 0.1
# fix
# 1. get specified player base data @done
# 2. simple data getter flow @done
# 
# version 1.0
# change log file to /Users/rnt/Develop/Logs/xbox_checker.log
# fix
# 1. shell array can't handle string with space, "%20" replaced.
# 2. the output data extension now is json
# 3. remove the temp variables with comment
# todo
# 1. create "gametag and xuid link file" @done
# 2. support more api @delay
# 3. game title id database @cancel @comment:this festure handled by python program
# 4. achievement database @cancel @comment:this festure handled by python program
#
# version 1.1
# fix
# 1. use relative path
# todo
# 1. use relative path @done
# 2. support more api @delay
# 

# log file settings
logfile="../log/xbox.checker.log"
timestamp=`date '+%s'`

function logger(){
    id=$1
    logpath=$logfile
    message=$2
    echo "start write log : "$1" : "$2 #id
    currenttime=`date "+%Y-%m-%d %H:%M:%S"` 
    echo $currenttime":operation-"$id" "$message >> $logpath
}

# input data settings
playeridfile="../config/gametags.txt"

# data floder settings
datafolder="../data/"
# 暂不使用该文件
playerdatafile="$datafolder/playerdata.txt"
# 玩家数据拉取之后单独保存到单个文件中
# 文件命名规则:
# 时间戳_{gametag}.json

# API settings
apifile="../config/api.config.ini"
apikey=$(cat $apifile | awk '{print $0}')
basecommand="curl -s -H \"X-AUTH: $apikey\""

# request urls
baseurl="https://xboxapi.com"
getXUID="$baseurl/v2/xuid/"
xboxoneGame1="$baseurl/v2/"  # {xuid}
xboxoneGame2="/xboxonegames"

function getSingleXoneGameData(){
    timestamp=`date '+%s'` # 单次操作时间戳(id)
    gametag=$1
    logger $timestamp "get player $gametag 's data"
    command=$basecommand" "$getXUID$gametag
    logger $timestamp "get player xuid , the command is "
    logger $timestamp "$command"
    # execute command to temp file 
    tempfile="temp$timestamp.txt"
    eval $command >> $tempfile
    xuid=$(cat $tempfile | awk '{print $0}')
    logger $timestamp "the player's xuid is $xuid"
    # 文件命名规则:
    # 时间戳_{gametag}_{xuid}.json
    filename=$datafolder$timestamp"_"$gametag"_"$xuid".json"
    command=$basecommand" "$xboxoneGame1$xuid$xboxoneGame2
    logger $timestamp "get player xboxone games data , the command is "
    logger $timestamp "$command"
    logger $timestamp "the data path is $filename"
    eval $command >> $filename
    # delete the temp file
    rm $tempfile
}

playerarray=($(cat $playeridfile | awk '{gsub(" ","%20",$0);print $0}'))
len=${#playerarray[@]}
for s in ${playerarray[@]}
do
    getSingleXoneGameData $s
done

echo "done"