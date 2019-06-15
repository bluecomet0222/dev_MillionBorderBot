import discord
import asyncio
import urllib.request
import json
import datetime
import time


###############################
# パラメータ一覧
###############################

BOT_TOKEN           = "NTA3MjE1ODM4NTA4NjEzNjQz.Drtdbw.4m56UuTFpeU7MIpwJzfrvusttnE"
TEXT_CHANNEL        = "545291639141171210"  # テキストチャットのチャンネルID
EventInfoChanel     = "588734619692695558"  # イベント情報チャットのチャンネルID
PersonRankingChanel = "588734676383039509"  # 個人ポイントチャットのチャンネルID
LoungeRankingChanel = "588742168970002439"  # ラウンジポイントチャットのチャンネルID
BorderBotErrorChanel = "588776428808699954" # ボーダーボットのエラーログ出力チャンネルID


#
# https://api.matsurihi.me/docs/
RequestURL = "https://api.matsurihi.me/mltd/v1/"    # APIのパス
RequestEventsURL = RequestURL + "events/"           # API_イベント用のフォルダ
GetPersonRankNumber = "1,2,3,4,5,6,7,8,9,10,11,98,99,100,101,2500,2501,5000"    # 個人取得ランキング
GetLoungeRankNumber = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"                     # ラウンジ取得ランキング
Interval = 60                                       # 60秒ごとにループする


# メッセージ一覧
StartUpMsg = "起動しました。"
NoEventMsg = "現在開催中のイベントはありません"

client = discord.Client() # 接続に使用するオブジェクト
#loop = asyncio.get_event_loop() # イベントループを取得
text_chat = discord.Object(id=TEXT_CHANNEL)
eventChat = discord.Object(id=EventInfoChanel)
personRankChat = discord.Object(id=PersonRankingChanel)
loungeRankChat = discord.Object(id=LoungeRankingChanel)
borderBotErrorChat = discord.Object(id=BorderBotErrorChanel)

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

    await client.send_message(eventChat, StartUpMsg)

    # 起動後にはイベント情報を取得する
    eventInfo = GetEventInfo()
    msg = NoEventMsg
    eventType = -1
    eventId = -1

    if eventInfo != "":
        # イベント情報メッセージは生成しない
        eventType = eventInfo['type']
        eventId = eventInfo['id']

    lastPersonBorderDate = ""
    lastLoungeBorderDate = ""

    while True:

        nowTime = datetime.datetime.now()
        # ToDo : デバッグ用
        nowTime = datetime.datetime(2019, 6, 13, 0, 0, 0)

        # 0時0分 または 15時(初日)ならば、イベント情報を出力する
        # 0時0分 ならば実行
        if nowTime.hour == 0 and nowTime.minute == 0:
            eventInfo = GetEventInfo()
            msg = NoEventMsg
            eventType = -1
            eventId = -1
            # 何かしら結果が返却されればイベント中と判断する
            if eventInfo != "":
                eventType = eventInfo['type']
                eventId = eventInfo['id']
                # イベント情報メッセージ生成
                msg = GetEventInfoMsg(eventInfo, nowTime)
                await client.send_message(eventChat, msg)

        # 15時5分ならば実行
        elif nowTime.hour == 15 and nowTime.minute == 5:
            # ここを実行する時間がイベント初日であれば出力する
            eventInfo = GetEventInfo()
            tmpArray = TimeConversion(eventInfo['schedule']['beginDate'])
            beginData = datetime.datetime.strptime(tmpArray[0], '%Y-%m-%d')

            if beginData.date() == nowTime.date() :
                msg = GetEventInfoMsg(eventInfo, nowTime)
                await client.send_message(eventChat, msg)

        await client.send_message(eventChat, nowTime)

        # 1.Typeを確認し、シアターもしくはツアーでならば実行
        if eventType == 3 or eventType == 4:

            # 個人ボーダー取得
            # 2.前回の更新から40分以上経過 or 初取得であれば実行
            # ランキング更新判定
            if ChkUpdateRanking(lastPersonBorderDate, nowTime, 40):

                # ポイントランキング取得
                type ="person"
                rankingInfo = GetEventPointPersonRanking(eventId, type, GetPersonRankNumber)

                # 前回出力した時刻と同じであれば出力しない
                dataCnt = len(rankingInfo[0]['data']) - 1
                if TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime']) != lastPersonBorderDate :
                    msg = GetEventPointRankingMsg(rankingInfo)
                    await client.send_message(personRankChat, msg)

                    # 取得時刻の追記
                    lastPersonBorderDate = TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime'])

                # if TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime']) != lastPersonBorderDate:
             # if ChkUpdateRanking(rankingInfo, lastDate):

            # ラウンジランキングボーダー取得
            # 2.前回の更新から35分以上経過 or 初取得であれば実行
            if ChkUpdateRanking(lastLoungeBorderDate, nowTime, 35):

                type ="lounge"
                rankingInfo = GetEventPointPersonRanking(eventId, type, GetLoungeRankNumber)

                # 前回出力した時刻と同じであれば出力しない
                dataCnt = len(rankingInfo[0]['data']) - 1
                if TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime']) != lastLoungeBorderDate :
                    msg = GetEventPointRankingMsg(rankingInfo)
                    await client.send_message(loungeRankChat, msg)

                    # 取得時刻の追記
                    lastLoungeBorderDate = TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime'])
                    print(lastLoungeBorderDate)
                #if TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime']) != lastPersonBorderDate:
            # if ChkUpdateRanking(lastLoungeBorderDate, nowTime, 35):

        # if eventType == 3 or eventType == 4:


        await asyncio.sleep(Interval)
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
   requestParams = "beginTime" + datetime.datetime.now().strftime("%Y-%m-%d")
   requestUrl = RequestEventsURL + "?" + requestParams
   """
   # =========テスト用=========
   # ToDo
   requestParams = "at=2019-06-05"
   requestUrl = RequestEventsURL + "?" + requestParams
   print(requestUrl)
   # =========テスト用=========
   """

   jsonDict = sendRequest(requestUrl)

   if len(jsonDict) != 0:
       lastEventNumber = len(jsonDict) - 1
       eventInfoJson = jsonDict[lastEventNumber]
       tmpArray = TimeConversion(eventInfoJson['schedule']['endDate'])

       # フォーマット変換
       endDate = datetime.datetime.strptime(tmpArray[0], '%Y-%m-%d')
       endTime = datetime.datetime.strptime(tmpArray[1], '%H:%M:%S')
       nowTime = datetime.datetime.now()

       # 現在の時刻を取得し比較する
       if endDate.date() < nowTime.date():
           eventInfoJson = ""
       elif endDate.date() == nowTime.date() and endTime.strftime("%H:%M:%S") < nowTime.strftime("%H:%M:%S"):
           eventInfoJson = ""
       """ 
       # =========テスト用=========
       # ToDo
       eventInfoJson = jsonDict[0]
       # =========テスト用=========
       """
    # if len(jsonDict) != 0:

   return eventInfoJson

# def get_event_info():

###################
# イベント情報解析
# 引数 : なし
# 戻り値 : イベント情報
###################
def GetEventInfoMsg(eventInfoJson, nowTime):

    # 取得後、出力する
    # イベントの開始時刻と終了時刻を取得する
    tmpArray = TimeConversion(eventInfoJson['schedule']['beginDate'])
    beginData = tmpArray[0]
    beginTime = tmpArray[1]

    tmpArray = TimeConversion(eventInfoJson['schedule']['endDate'])
    endData = tmpArray[0]
    endTime = tmpArray[1]


    # 取得日時
    getEventInfo = ""
    getEventInfo += "取得日時        :" + nowTime.strftime('%Y-%m-%d %H:%M:%S') + "\n"

    # 経過時間の逆算



    # イベント情報
    eventInfo = ""
    eventInfo += "イベント名     ： " + eventInfoJson['name'] + "\n"
    eventInfo += "イベント期間   ： " + beginData + " " + beginTime + " ~ " + endData + " " + endTime + "\n"

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
    msg += getEventInfo
    msg += eventInfo
    msg += boostInfo
    msg += "```" + "\n"

    return msg
#def GetEventInfoMsg(eventInfoJson):


#########################
# ランキング情報取得関数
# 引数： ID
#     ： タイプ(個人 or ラウンジ)
#     ： 順位
# 戻り値：APIから取得したポイントランキング情報
#########################
def GetEventPointPersonRanking(getId, type, ranking):

    rankingPath = "/rankings/logs/"
    if type == "person" :
        rankingPath += "eventPoint/"
    elif type == "lounge" :
        rankingPath += "loungePoint/"

    # ex) https://api.matsurihi.me/mltd/v1/events/33/rankings/logs/eventPoint/1,2,3
    requestUrl = RequestEventsURL + "/" + str(getId) + rankingPath + ranking
    jsonDict = sendRequest(requestUrl)

    return jsonDict

#def get_event_point_ranking(now_time):

#########################
# リクエスト送信関数
# 引数：リクエスト送信先URL
#########################
def sendRequest(requestUrl):

    req = urllib.request.Request(requestUrl)
    json_dict = ""
    try :
        with urllib.request.urlopen(req) as res:
            body = res.read()

            # 配列で取得される。1つ目の要素を取得
            json_dict = json.loads(body)
            #json_dict = json_dict[0]

    except urllib.error.HTTPError as e:
        print('raise HTTPError')
        print(e.code)
        print(e.reason)
    except urllib.error.ConnectionError as e:
        print('rase ConnectionError')
        print(e.reason)
    except  :
        print('Except')

    return json_dict


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
def ChkUpdateRanking(lastDataTime, nowTime, addMinitu = 0):

    updateFlg = False
    if lastDataTime == "" :
        updateFlg = True

    else :

        summaryDate = datetime.datetime.strptime(lastDataTime[0], '%Y-%m-%d')
        summaryTime = datetime.datetime.strptime(lastDataTime[1], '%H:%M:%S')

        nextTime = datetime.datetime(summaryDate.year, summaryDate.month, summaryDate.day, summaryTime.hour, summaryTime.minute, summaryTime.second)
        nextTime = nextTime + datetime.timedelta(minutes=addMinitu)

        # 現在時刻とデータ更新時刻＋40分の時刻を比較し
        # 超えていれば再取得を行う
        if nextTime.date() < nowTime.date():
            updateFlg = True
        elif nextTime.date() == nowTime.date() and nextTime.strftime("%H:%M:%S") < nowTime.strftime("%H:%M:%S"):
            updateFlg = True

    return updateFlg

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
            msg += str(get_rank) + "位:  " + str(now_score) + "pt ( +" + str(diff_score) + "pt )"+ "\n"

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