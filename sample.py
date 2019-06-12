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
GetRankNumber = "1,2,3,100,101,2500,5000"
EventType = -1

"""
APIVersion = "version/latest"
EventType = "/rankings/logs/eventPoint/"
GetRunkinNum
"""

client = discord.Client() # 接続に使用するオブジェクト
loop = asyncio.get_event_loop() # イベントループを取得
text_chat = discord.Object(id=TEXT_CHANNEL)


###############################
# クライアントイベント
###############################
@client.event
async def on_ready():
    print('ログインしました')
    asyncio.ensure_future(greeting_gm(), loop=loop)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def greeting_gm():

    await client.send_message(text_chat, '起動しました。')

    # 起動後にはイベント情報を取得する
    # イベント情報取得
    eventInfo = GetEventInfo()

    if eventInfo == "":
        msg = "現在開催中のイベントはありません"
    else:
        eventType = eventInfo['type']
        eventId = eventInfo['id']
        # イベント情報メッセージ生成
        msg = GetEventInfoMsg(eventInfo)
    await client.send_message(text_chat, msg)

    lastDate = ""

    while True:
        """
        # 起動後にはイベント情報を取得する
        # イベント情報取得
        eventInfo = GetEventInfo()

        if eventInfo == "":
            msg = "現在開催中のイベントはありません"
        else:
            eventType = eventInfo['type']
            eventId = eventInfo['id']
            # イベント情報メッセージ生成
            msg = GetEventInfoMsg(eventInfo)
        await client.send_message(text_chat, msg)
        """

        nowTime = datetime.datetime.now()

        # ToDo : 00:00ならイベント情報を再取得する
        if nowTime.hour == "0" and nowTime.minute == "0":
            eventInfo = GetEventInfo()
            if eventInfo == "":
                msg = "現在開催中のイベントはありません"
            else:
                eventType = eventInfo['type']
                eventId = eventInfo['id']
                # イベント情報メッセージ生成
                msg = GetEventInfoMsg(eventInfo)

        # 次の取得時刻の計算
        await client.send_message(text_chat, nowTime)

        # 1.Typeを確認し、シアターもしくはツアーでならば実行
        # ミリコレ、ワーキングなら実行しない
        # if eventType == 3 or eventType == 4:
        if eventType == 3 or eventType == 4:

            # 2.前回の更新から40分以上経過 or 初取得であれば実行
            if lastDate == "":

                # 取得処理開始
                # ポイントランキング取得
                rankingInfo = GetEventPointRanking(eventId)
                # ランキング更新判定
                if ChkUpdateRanking(rankingInfo, lastDate):
                    msg = GetEventPointRankingMsg(rankingInfo)
                    await client.send_message(text_chat, msg)

                    # 取得時刻の追記
                    dataCnt = len(rankingInfo[0]['data']) - 1
                    lastDate = TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime'])
                    print(lastDate)
                # if ChkUpdateRanking(rankingInfo, lastDate):
            # if lastDate == "" :
        # if eventType == 3 or eventType == 4:

        # 60秒ごとにループする
        interval = 60
        await asyncio.sleep(interval)
    #time.sleep(interval)


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
   # 注意：時刻指定の場合、イベント開始日にはAPIが対応していない模様
   #       なので、イベント情報をすべて引っ張ってきて最後のidの情報の終了日が今の日付より前ならイベントありと判断する
   orderBy = "beginTime" + datetime.datetime.now().strftime("%Y-%m-%d")
   requestUrl = RequestEventsURL + "?" + orderBy
   reqeustAction = urllib.request.Request(requestUrl)

   with urllib.request.urlopen(reqeustAction) as responceData:
       body = responceData.read()

       # 配列で取得される。1つ目の要素を取得
       jsonDict = json.loads(body)
       if len(jsonDict) == 0:
           eventInfoJson = ""
       else :
            lastEventNumber = len(jsonDict) - 1
            print(len(jsonDict))
            eventInfoJson = jsonDict[lastEventNumber]
            tmpArray = TimeConversion(eventInfoJson['schedule']['endDate'])

            # フォーマット変換
            endDate = datetime.datetime.strptime(tmpArray[0], '%Y-%m-%d')
            endTime = datetime.datetime.strptime(tmpArray[1], '%H:%M:%S')
            nowTime = datetime.datetime.now()

            # 現在の時刻を取得し比較する
            if endDate.date() <= nowTime.date() and endTime.strftime("%H:%M:%S") < nowTime.strftime("%H:%M:%S") :
                eventInfoJson = ""

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
# ランキング情報取得関数
# 引数：時刻
# 戻り値：APIから取得したポイントランキング情報
#########################
def GetEventPointRanking(getId):

    # ex) https://api.matsurihi.me/mltd/v1/events/33/rankings/logs/eventPoint/1,2,3
    requestUrl = RequestEventsURL + "/" + str(getId) + "/rankings/logs/eventPoint/" + GetRankNumber
    req = urllib.request.Request(requestUrl)

    with urllib.request.urlopen(req) as res:
        body = res.read()

        # 配列で取得される。1つ目の要素を取得
        json_dict = json.loads(body)
        #json_dict = json_dict[0]
    return json_dict

#def get_event_point_ranking(now_time):

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

#########################
# ポイントランキング更新判定関数
# 引数：ランキング情報, 最終日時
# 戻り値：boolean true 更新されている false 更新されていない
#########################
def ChkUpdateRanking(getRanking, lastTime):

    dataCnt= len(getRanking[0]['data']) - 1
    tmpArray = TimeConversion(getRanking[0]['data'][dataCnt]['summaryTime'])
    updateChkFlg = False

    if lastTime == "" :
        updateChkFlg = True
    elif tmpArray[0] != lastTime[0] or  tmpArray[1] != lastTime[1] :
        updateChkFlg = True

    return updateChkFlg

#########################
# ランキング情報整形関数
# 引数：APIから取得したポイントランキング
# 戻り値：メッセージ
#########################
def GetEventPointRankingMsg(getRanking):

    data_cnt= len(getRanking[0]['data']) - 1
    tmp_ary = TimeConversion(getRanking[0]['data'][data_cnt]['summaryTime'])

    msg = ""
    msg += "```" + "\n"
    msg += "取得日時:" + tmp_ary[0]  +" " + tmp_ary[1] + "\n"

    for get_rank_data in getRanking :
        get_rank = get_rank_data['rank']
        get_data = get_rank_data['data']

        if len(get_data) > 2:
            now_data = get_data[len(get_data) - 1]
            old_data = get_data[len(get_data) - 2]
            now_score = int(now_data['score'])
            old_score = int(old_data['score'])
            diff_score = now_score - old_score
            msg += str(get_rank) + "位:  " + str(now_score) + "pt ( +" + str(diff_score) + "pt)"+ "\n"

        #else :

    # for get_rank_data in get_ranking :
    msg += "```"+ "\n"
    return msg

#get_event_point_ranking_msg():

###############################
# ボット起動
###############################

# botの接続と起動
# （BOT_TOKENにはbotアカウントのアクセストークンを入れてください）
client.run(BOT_TOKEN)