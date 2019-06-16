import discord
import asyncio
import datetime
import EventInfomation


###############################
# パラメータ一覧
###############################

# サーバ定数
BotToken            = "NTA3MjE1ODM4NTA4NjEzNjQz.Drtdbw.4m56UuTFpeU7MIpwJzfrvusttnE"
Text_Channel         = "545291639141171210"  # テキストチャットのチャンネルID
EventInfoChanel      = "588734619692695558"  # イベント情報チャットのチャンネルID
PersonRankingChanel  = "588734676383039509"  # 個人ポイントチャットのチャンネルID
LoungeRankingChanel  = "588742168970002439"  # ラウンジポイントチャットのチャンネルID
BorderBotErrorChanel = "588776428808699954" # ボーダーボットのエラーログ出力チャンネルID

# 実行感覚
Interval = 60                                       # 60秒ごとにループする

# メッセージ一覧
StartUpMsg = "起動しました。"
NoEventMsg = "現在開催中のイベントはありません"

client = discord.Client() # 接続に使用するオブジェクト

# 各チャットのオブジェクト
text_chat = discord.Object(id=Text_Channel)
eventChat = discord.Object(id=EventInfoChanel)
personRankChat = discord.Object(id=PersonRankingChanel)
loungeRankChat = discord.Object(id=LoungeRankingChanel)
borderBotErrorChat = discord.Object(id=BorderBotErrorChanel)


###############################
# クライアントイベント開始
###############################
@client.event
async def on_ready():
    print('ログインしました')
    # 通常イベント
    eventInfo = EventInfomation.EventInfomation()
    asyncio.ensure_future(greeting_gm(eventInfo))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

###############################
#  設定情報表示
###############################
@client.event
async def on_message(message):
    if message.author != client.user:
        msg = message.author.mention + " Hi."
        await client.send_message(eventChat, msg)


###############################
#  イベント関連出力
###############################
@client.event
async def greeting_gm(_eventInfo):

    await client.send_message(eventChat, StartUpMsg)

    # 起動後にはイベント情報を取得する
    eventInfo = _eventInfo.GetEventInfo()
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

        # 0時0分 または 15時(初日)ならば、イベント情報を出力する
        # 0時0分 ならば実行
        if nowTime.hour == 0 and nowTime.minute == 0:
            eventInfo = _eventInfo.GetEventInfo()
            msg = NoEventMsg
            eventType = -1
            eventId = -1
            # 何かしら結果が返却されればイベント中と判断する
            if eventInfo != "":
                eventType = eventInfo['type']
                eventId = eventInfo['id']
                # イベント情報メッセージ生成
                msg = _eventInfo.GetEventInfoMsg(eventInfo, nowTime)
                await client.send_message(eventChat, msg)

        # 15時5分ならば実行
        elif nowTime.hour == 15 and nowTime.minute == 5:
            # ここを実行する時間がイベント初日であれば出力する
            eventInfo = _eventInfo.GetEventInfo()
            tmpArray = _eventInfo.getBeginTime(eventInfo)
            beginData = datetime.datetime.strptime(tmpArray[0], '%Y-%m-%d')

            if beginData.date() == nowTime.date() :
                msg = _eventInfo.GetEventInfoMsg(eventInfo, nowTime)
                await client.send_message(eventChat, msg)

        # ToDo:デバッグ用
        #await client.send_message(eventChat, nowTime)

        # 1.Typeを確認し、シアターもしくはツアーでならば実行
        if eventType == 3 or eventType == 4:

            # 個人ボーダー取得
            # 2.前回の更新から40分以上経過 or 初取得であれば実行
            # ランキング更新判定
            if _eventInfo.ChkUpdateRanking(lastPersonBorderDate, nowTime, 40):

                # ポイントランキング取得
                type ="person"
                rankingInfo = _eventInfo.GetEventPointPersonRanking(eventId, type)

                # 前回出力した時刻と同じであれば出力しない
                getSummayTime = _eventInfo.getSummaryTime(rankingInfo)
                if  getSummayTime != lastPersonBorderDate :
                    msg = _eventInfo.GetEventPointRankingMsg(rankingInfo)
                    await client.send_message(personRankChat, msg)

                    # 取得時刻の追記
                    lastPersonBorderDate = getSummayTime

                # if TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime']) != lastPersonBorderDate:
             # if ChkUpdateRanking(rankingInfo, lastDate):

            # ラウンジランキングボーダー取得
            # 2.前回の更新から35分以上経過 or 初取得であれば実行
            if _eventInfo.ChkUpdateRanking(lastLoungeBorderDate, nowTime, 35):

                type ="lounge"
                rankingInfo = _eventInfo.GetEventPointPersonRanking(eventId, type)

                # 前回出力した時刻と同じであれば出力しない
                getSummayTime = _eventInfo.getSummaryTime(rankingInfo)
                if getSummayTime != lastLoungeBorderDate :
                    msg = _eventInfo.GetEventPointRankingMsg(rankingInfo)
                    await client.send_message(loungeRankChat, msg)

                    # 取得時刻の追記
                    lastLoungeBorderDate = getSummayTime
                #if TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime']) != lastPersonBorderDate:
            # if ChkUpdateRanking(lastLoungeBorderDate, nowTime, 35):

        # if eventType == 3 or eventType == 4:


        await asyncio.sleep(Interval)
    #time.sleep(interval)

###############################
# ボット起動
###############################

# botの接続と起動
# （BotTokenにはbotアカウントのアクセストークンを入れてください）
client.run(BotToken)