import datetime
import Common

class EventInfomation:
    #
    # https://api.matsurihi.me/docs/
    RequestURL = "https://api.matsurihi.me/mltd/v1/"  # APIのパス
    RequestEventsURL = RequestURL + "events/"  # API_イベント用のフォルダ
    GetPersonRankNumber = "1,2,3,4,5,6,7,8,9,10,11,98,99,100,101,2500,2501,5000"  # 個人取得ランキング
    GetLoungeRankNumber = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"  # ラウンジ取得ランキング
    Interval = 60  # 60秒ごとにループする
    SpaceCount = 10
    DiffSpaceCount = 7
    common = Common.Common()

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

        jsonDict = self.common.sendRequest(requestUrl)

        if len(jsonDict) != 0:
            lastEventNumber = len(jsonDict) - 1
            eventInfoJson = jsonDict[lastEventNumber]
            tmpArray = self.common.TimeConversion(eventInfoJson['schedule']['endDate'])

            # フォーマット変換
            endDate = datetime.datetime.strptime(tmpArray[0], '%Y-%m-%d')
            endTime = datetime.datetime.strptime(tmpArray[1], '%H:%M:%S')
            nowTime = datetime.datetime.now()

            # 現在の時刻を取得し比較する
            if endDate.date() < nowTime.date():
                eventInfoJson = ""
            elif endDate.date() == nowTime.date() and endTime.strftime("%H:%M:%S") < nowTime.strftime("%H:%M:%S"):
                eventInfoJson = ""
        # if len(jsonDict) != 0:

        return eventInfoJson
    # def get_event_info():

    ###################
    # イベント情報解析
    # 引数 : なし
    # 戻り値 : イベント情報
    ###################
    def GetEventInfoMsg(self, eventInfoJson, nowTime):

        # 取得後、出力する
        # イベントの開始時刻と終了時刻を取得する
        tmpArray = self.common.TimeConversion(eventInfoJson['schedule']['beginDate'])
        beginDay = datetime.datetime.strptime(tmpArray[0], '%Y-%m-%d')
        beginTime = datetime.datetime.strptime(tmpArray[1], '%H:%M:%S')

        tmpArray = self.common.TimeConversion(eventInfoJson['schedule']['endDate'])
        endDay = datetime.datetime.strptime(tmpArray[0], '%Y-%m-%d')
        endTime = datetime.datetime.strptime(tmpArray[1], '%H:%M:%S')

        beginData = datetime.datetime(beginDay.year, beginDay.month, beginDay.day, beginTime.hour, beginTime.minute,
                                      beginTime.second)
        endData = datetime.datetime(endDay.year, endDay.month, endDay.day, endTime.hour, endTime.minute, endTime.second)

        # 取得日時
        # 経過時間の逆算
        # 秒単位で計算する
        totalEventTime = (endData - beginData).total_seconds()
        elapsedTime = (nowTime - beginData).total_seconds()
        ruuningRercantage = (elapsedTime / totalEventTime) * 100
        getEventInfo = ""
        getEventInfo += "取得日時       :  " + nowTime.strftime('%Y-%m-%d %H:%M:%S') + " (" + str(
            round(ruuningRercantage, 2)) + "%)" + "\n"

        # イベント情報
        eventInfo = ""
        eventInfo += "イベント名     ： " + eventInfoJson['name'] + "\n"
        eventInfo += "イベント期間   ： " + beginData.strftime('%Y-%m-%d %H:%M:%S') + "  ~  " + endData.strftime(
            '%Y-%m-%d %H:%M:%S') + "\n"

        boostInfo = ""

        # 後半戦があれば追加
        if eventInfoJson['type'] == 3 or eventInfoJson['type'] == 4:
            tmpArray = self.common.TimeConversion(eventInfoJson['schedule']['boostBeginDate'])
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

    # def GetEventInfoMsg(eventInfoJson):

    #########################
    # ランキング情報取得関数
    # 引数： ID
    #     ： タイプ(個人 or ラウンジ)
    #     ： 順位
    # 戻り値：APIから取得したポイントランキング情報
    #########################
    def GetEventPointPersonRanking(self, getId, type):

        ranking = self.GetPersonRankNumber
        rankingPath = "/rankings/logs/"
        if type == "person":
            rankingPath += "eventPoint/"
        elif type == "lounge":
            rankingPath += "loungePoint/"
            ranking = self.GetLoungeRankNumber

        # ex) https://api.matsurihi.me/mltd/v1/events/33/rankings/logs/eventPoint/1,2,3
        requestUrl = self.RequestEventsURL + "/" + str(getId) + rankingPath + ranking
        jsonDict = self.common.sendRequest(requestUrl)

        return jsonDict

    # def get_event_point_ranking(now_time):

    #########################
    # ポイントランキング更新判定関数
    # 引数：ランキング情報, 最終日時
    # 戻り値：boolean true 更新されている false 更新されていない
    #########################
    def ChkUpdateRanking(self, lastDataTime, nowTime, addMinitu=0):

        updateFlg = False
        if lastDataTime == "":
            updateFlg = True

        else:

            summaryDate = datetime.datetime.strptime(lastDataTime[0], '%Y-%m-%d')
            summaryTime = datetime.datetime.strptime(lastDataTime[1], '%H:%M:%S')

            nextTime = datetime.datetime(summaryDate.year, summaryDate.month, summaryDate.day, summaryTime.hour,
                                         summaryTime.minute, summaryTime.second)
            nextTime = nextTime + datetime.timedelta(minutes=addMinitu)

            # 現在時刻とデータ更新時刻＋40分の時刻を比較し
            # 超えていれば再取得を行う
            if nextTime.date() < nowTime.date():
                updateFlg = True
            elif nextTime.date() == nowTime.date() and nextTime.strftime("%H:%M:%S") < nowTime.strftime("%H:%M:%S"):
                updateFlg = True

        return updateFlg
    # def ChkUpdateRanking(lastDataTime, nowTime, addMinitu=0):

    #########################
    # ランキング情報整形関数
    # 引数：APIから取得したポイントランキング
    # 戻り値：メッセージ
    #########################
    def GetEventPointRankingMsg(self, getRanking):

        data_cnt = len(getRanking[0]['data']) - 1
        tmp_ary = self.common.TimeConversion(getRanking[0]['data'][data_cnt]['summaryTime'])

        msg = ""
        msg += "```" + "\n"
        msg += "取得日時:" + tmp_ary[0] + " " + tmp_ary[1] + "\n"

        for get_rank_data in getRanking:
            get_rank = get_rank_data['rank']
            get_data = get_rank_data['data']

            if len(get_data) > 2:
                now_data = get_data[len(get_data) - 1]
                old_data = get_data[len(get_data) - 2]
                now_score = int(now_data['score'])
                old_score = int(old_data['score'])
                diff_score = now_score - old_score


                # 余白の逆算をする
                spaceCount = self.SpaceCount - len(str(get_rank)) - len(str(now_score))
                diffSpaceCount = self.DiffSpaceCount - len(str(diff_score))
                space = ""
                diffSpace = ""

                for i in range(spaceCount) :
                    space += " "

                for i in range(diffSpaceCount) :
                    diffSpace += " "

                msg += str(get_rank) + "位: " + space + str(now_score) + "pt (+" + diffSpace + str(diff_score) + "pt)" + "\n"

            # else :

        # for get_rank_data in get_ranking :
        msg += "```" + "\n"
        return msg

    # get_event_point_ranking_msg():

    ###################
    # イベント開始時刻取得関数
    # 引数 : なし
    # 戻り値 : 更新日時
    ###################
    def getBeginTime(self, rankingInfo):
        dataCnt = len(rankingInfo[0]['data']) - 1
        getBeginTime = self.common.TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime'])

        return getBeginTime
    #  def getBeginTime(self, rankingInfo):

    ###################
    # 更新時刻取得関数
    # 引数 : なし
    # 戻り値 : 更新日時
    ###################
    def getSummaryTime(self, rankingInfo):
        dataCnt = len(rankingInfo[0]['data']) - 1
        getSummayTime = self.common.TimeConversion(rankingInfo[0]['data'][dataCnt]['summaryTime'])

        return getSummayTime
    #  def getSummaryTime(self, rankingInfo):


    ###################
    # イベント情報取得関数
    # 引数 : なし
    # 戻り値 : イベント情報
    ###################
    def test_GetEventInfo(self):
        # ex) https://api.matsurihi.me/mltd/v1/events?type=theater&at=2019-02-09
        # 注意：時刻指定の場合、イベント開始日にはAPIが対応していない模様
        #       なので、イベント情報をすべて引っ張ってきて最後のidの情報の終了日が今の日付より前ならイベントありと判断する
        requestParams = "beginTime" + datetime.datetime.now().strftime("%Y-%m-%d")
        requestUrl = self.RequestEventsURL + "?" + requestParams
        # =========テスト用=========
        # ToDo
        requestParams = "at=2019-06-05"
        requestUrl = self.RequestEventsURL + "?" + requestParams
        # =========テスト用=========

        jsonDict = self.common.sendRequest(requestUrl)
        if len(jsonDict) != 0:
            lastEventNumber = len(jsonDict) - 1
            eventInfoJson = jsonDict[lastEventNumber]
            tmpArray = self.common.TimeConversion(eventInfoJson['schedule']['endDate'])

            # フォーマット変換
            endDate = datetime.datetime.strptime(tmpArray[0], '%Y-%m-%d')
            endTime = datetime.datetime.strptime(tmpArray[1], '%H:%M:%S')
            nowTime = datetime.datetime.now()

            # 現在の時刻を取得し比較する
            if endDate.date() < nowTime.date():
                eventInfoJson = ""
            elif endDate.date() == nowTime.date() and endTime.strftime("%H:%M:%S") < nowTime.strftime("%H:%M:%S"):
                eventInfoJson = ""

            # =========テスト用=========
            # ToDo
            eventInfoJson = jsonDict[0]
            # =========テスト用=========

        return eventInfoJson

    #def test_GetEventInfo(self):
