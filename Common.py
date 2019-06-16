import urllib.request
import json

class Common :

    def __init__(self):
        pass

    #########################
    # リクエスト送信関数
    # 引数：リクエスト送信先URL
    #########################
    def sendRequest(self, requestUrl):

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
        except OSError as e:
            print('rase OSError')
            print(e.reason)
        except:
            print('Except')

        return json_dict
    # def sendRequest(requestUrl):

    #########################
    # 時刻変換関数
    # 引数：date_time APIから取得したイベント時刻
    #########################
    def TimeConversion(self,date_time):
        return_ary = []
        tmp_ary = date_time.split('T')
        tmp_ary2 = tmp_ary[1].split('+')
        return_ary.append(tmp_ary[0])
        return_ary.append(tmp_ary2[0])

        return return_ary
    # def TimeConversion(date_time):