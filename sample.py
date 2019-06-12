import discord
import asyncio
import urllib.request
import json
import datetime
import time


###############################
# パラメータ一覧
###############################

BOT_TOKEN = "NTA3MjE1ODM4NTA4NjEzNjQz.Drtdbw.4m56UuTFpeU7MIpwJzfrvusttnE"
TEXT_CHANNEL = "545291639141171210" # テキストチャットのチャンネルID

#
# https://api.matsurihi.me/docs/
RequestURL = "https://api.matsurihi.me/mltd/v1/"
RequestEventsURL = RequestURL + "events/"
"""
APIVersion = "version/latest"
EventType = "/rankings/logs/eventPoint/"
GetRunkinNum
"""

client = discord.Client() # 接続に使用するオブジェクト
text_chat = discord.Object(id=TEXT_CHANNEL)


###############################
# クライアントイベント
###############################
@client.event
async def on_ready():
    print('ログインしました')
    asyncio.ensure_future(greeting_gm())
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def greeting_gm():
    await client.send_message(text_chat, '起動しました。')
    """
    eventInfo = GetEventInfo()
    msg = GetEventInfoMsg(eventInfo)
    await client.send_message(text_chat, msg)
    """

    cnt = 0
    lastDate = ""
    while cnt == 0:
        nowTime = datetime.datetime.now().timedelta(hours=9)
        event_type = -1

        # 次の取得時刻の計算
        await client.send_message(text_chat, nowTime)

        # テストとして1分ごとにループする
        interval = 10
        time.sleep(interval)

    # while true :

###############################
# 各種関数
###############################

###################
# イベント情報取得関数
# 引数 : なし
# 戻り値 : イベント情報
###################
def GetEventInfo():
   # ex) https://api.matsurihi.me/mltd/v1/events?type=theater&at=2019-02-09
   AT = "at=" + datetime.datetime.now().strftime("%Y-%m-%d")
   reqeustAction = urllib.request.Request(RequestEventsURL + "?" + AT)

   with urllib.request.urlopen(reqeustAction) as responceData:
       body = responceData.read()

       # 配列で取得される。1つ目の要素を取得
       jsonDict = json.loads(body)
       if len(jsonDict) == 0:
           eventInfoJson = ""
       else :
            eventInfoJson = jsonDict[0]

   return eventInfoJson
# def get_event_info():

###################
# イベント情報解析
# 引数 : なし
# 戻り値 : イベント情報
###################
def GetEventInfoMsg(eventInfoJson):

    # 取得後、出力する
    # イベントの開始時刻と終了時刻を取得する
    tmpArray = TimeConversion(eventInfoJson['schedule']['beginDate'])
    beginData = tmpArray[0]
    beginTime = tmpArray[1]

    tmpArray = TimeConversion(eventInfoJson['schedule']['endDate'])
    endData = tmpArray[0]
    endTime = tmpArray[1]

    eventInfo = ""
    eventInfo += "イベント名 ： " + eventInfoJson['name'] + "\n"
    eventInfo += "イベント期間 ： " + beginData + " " + beginTime + " ~ " + endData + " " + endTime + "\n"

    boostInfo = ""

    # 後半戦があれば追加
    if eventInfoJson['type'] == 3 or eventInfoJson['type'] == 4:
        tmpArray = TimeConversion(eventInfoJson['schedule']['boostBeginDate'])
        boostData = tmpArray[0]
        boostTime = tmpArray[1]
        boostInfo = "後半戦開始日時 ： " + boostData + " " + boostTime + "\n"
        # eventInfoJson['type'] == 3  or eventInfoJson['type'] == 4 :

    # メッセージ追加
    msg = ""
    msg += "```" + "\n"
    msg += "=======================================================================" + "\n"
    msg += eventInfo
    msg += boostInfo
    msg += "=======================================================================" + "\n"
    msg += "```" + "\n"

    return msg
#def GetEventInfoMsg(eventInfoJson):

#########################
# 時刻変換関数
# 引数：date_time APIから取得したイベント時刻
#########################
def TimeConversion(date_time):
    return_ary = []
    tmp_ary = date_time.split('T')
    tmp_ary2 = tmp_ary[1].split('+')
    return_ary.append(tmp_ary[0])
    return_ary.append(tmp_ary2[0])

    return return_ary





###############################
# ボット起動
###############################

# botの接続と起動
# （BOT_TOKENにはbotアカウントのアクセストークンを入れてください）
client.run(BOT_TOKEN)