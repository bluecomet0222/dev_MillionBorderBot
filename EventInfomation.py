import discord
import asyncio
import urllib.request
import json
import datetime
import testClass
import time



class EventInfomation:
    #
    # https://api.matsurihi.me/docs/
    RequestURL = "https://api.matsurihi.me/mltd/v1/"  # APIのパス
    RequestEventsURL = RequestURL + "events/"  # API_イベント用のフォルダ
    GetPersonRankNumber = "1,2,3,4,5,6,7,8,9,10,11,98,99,100,101,2500,2501,5000"  # 個人取得ランキング
    GetLoungeRankNumber = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"  # ラウンジ取得ランキング
    Interval = 60  # 60秒ごとにループする

    ###################
    # コンストラクタ
    ###################
    def __init__(self):
        pass


    ###################
    # イベント情報取得関数
    # 引数 : なし
    # 戻り値 : イベント情報
    ###################
    def GetEventInfo(self):
        # ex) https://api.matsurihi.me/mltd/v1/events?type=theater&at=2019-02-09
        # 注意：時刻指定の場合、イベント開始日にはAPIが対応していない模様
        #       なので、イベント情報をすべて引っ張ってきて最後のidの情報の終了日が今の日付より前ならイベントありと判断する
        requestParams = "beginTime" + datetime.datetime.now().strftime("%Y-%m-%d")
        requestUrl = self.RequestEventsURL + "?" + requestParams
        """
        # =========テスト用=========
        # ToDo
        requestParams = "at=2019-06-05"
        requestUrl = RequestEventsURL + "?" + requestParams
        print(requestUrl)
        # =========テスト用=========
        """

        jsonDict = EventInfomation.sendRequest(requestUrl)

        if len(jsonDict) != 0:
            lastEventNumber = len(jsonDict) - 1
            eventInfoJson = jsonDict[lastEventNumber]
            tmpArray = EventInfomation.TimeConversion(eventInfoJson['schedule']['endDate'])

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

    #########################
    # リクエスト送信関数
    # 引数：リクエスト送信先URL
    #########################
    def sendRequest(requestUrl):

        req = urllib.request.Request(requestUrl)
        json_dict = ""
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()

                # 配列で取得される。1つ目の要素を取得
                json_dict = json.loads(body)
                # json_dict = json_dict[0]

        except urllib.error.HTTPError as e:
            print('raise HTTPError')
            print(e.code)
            print(e.reason)
        except urllib.error.ConnectionError as e:
            print('rase ConnectionError')
            print(e.reason)
        except:
            print('Except')

        return json_dict
    # def sendRequest(requestUrl):

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
    # def TimeConversion(date_time):

