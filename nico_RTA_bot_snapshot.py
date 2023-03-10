# 公式
import datetime
import json

# サードパーティ
from mastodon import Mastodon
import requests
import tweepy
from twitter_text import parse_tweet

# 自作
import nico_getthumbinfo as thumb_info
from secret import TwitterAPI
from secret import MastodonAPI

def searchRtaSnapshotApi(begin_datetime, end_datetime) -> list:
    """リアル登山アタック動画を Snapshot API 経由で検索し、結果を返す

    参考: Qiita - python:requestsでニコニコ動画APIを使う
    https://qiita.com/be_tiger/items/a086380121a5cefe6eef
    """

    # APIのエンドポイント
    url = "https://api.search.nicovideo.jp/api/v2/snapshot/video/contents/search"

    # 抽出条件の指定
    json_filter = json.dumps(
        {
            "type": "range",
            "field": "startTime",
            "from": begin_datetime.isoformat(timespec="seconds"),
            "to": end_datetime.isoformat(timespec="seconds"),
            "include_lower": True
        }
    )
    # print(json_filter)

    # 並び替え条件の設定
    query_param = {
        "q": "RTA(リアル登山アタック) OR RTA(リアル登山アタック)外伝 OR RTA(リアル登山アタック)団体戦 OR RTA(リアル登山アタック)技術部",
        "targets": "tags",
        "fields": "contentId",
        "jsonFilter": json_filter,
        "_sort": "-startTime",  # 投稿が新しい順
        "_limit": 50,
    }

    # カスタムヘッダの指定（指定が推奨されているらしい）
    headers = {"User-Agent": "RealTozanAttack-TwitterBot"}

    # API の実行
    res = requests.get(url, params=query_param, headers=headers)

    # 正常に取得できなかった場合は空のリストを返す
    if res.status_code != requests.codes.ok or res.json()["meta"]["status"] != 200:
        return []

    # 正常取得時の応答文字列
    """
    {'data': [{'contentId': 'sm41705968'},
            {'contentId': 'sm41701466'},
            {'contentId': 'sm41700684'},
            {'contentId': 'sm41686885'},
            {'contentId': 'sm41687602'},
            {'contentId': 'sm41687114'},
            {'contentId': 'sm41686241'},
            {'contentId': 'sm41678864'},
            {'contentId': 'sm41678019'},
            {'contentId': 'sm41676393'}],
    'meta': {'id': '5ece8017-1c75-4c0c-8414-564175237077',
            'status': 200,
            'totalCount': 3005}}
    """

    contents_ids = [str(x["contentId"]) for x in res.json()["data"]]
    return contents_ids

def tweet_RTA(sminfo: thumb_info):
    """指定した動画をTwitterでツイートする"""
    text1 = ""
    # text1 += "テスト投稿\n"
    text1 += "《 #リアル登山アタック 昨日の新着動画》\n"
    text1 += sminfo.getTitle() + "\n"
    text1 += "投稿者: %s" % sminfo.getAuthor() + " さん\n"
    
    text3 = ""
    text3 += "#%s" % sminfo.sm_id + "\n"
    text3 += sminfo.getURL()

    # タグの量によっては140文字制限を超えるため、調節する
    tweet_text = text1 + text3
    tags = sminfo.getTags()
    for i in range(1, len(tags)+1):
        text2 = "タグ: " + " ".join(tags[:i]) + "\n"
        temp = text1 + text2 + text3
        if parse_tweet(temp).valid:
            tweet_text = text1 + text2 + text3
        else:
            break

    # 認証と投稿
    auth = tweepy.OAuthHandler(TwitterAPI.consumer_key, TwitterAPI.consumer_secret)
    auth.set_access_token(TwitterAPI.access_token, TwitterAPI.access_token_secret)
    # api = tweepy.API(auth)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    api.update_status(status=tweet_text)


def toot_RTA(sminfo: thumb_info):
    """指定した動画をマストドンでトゥートする"""

    text = ""
    # text += "テスト投稿\n"
    text += "《 #リアル登山アタック 昨日の新着動画》\n"
    text += sminfo.getTitle() + "\n"
    text += "投稿者: %s" % sminfo.getAuthor() + " さん\n"
    text += "タグ: " + (" ".join(sminfo.getTags())) + "\n"
    text += "#%s" % sminfo.sm_id + "\n"
    text += sminfo.getURL()

    api = Mastodon(
        api_base_url  = MastodonAPI.server,
        client_id     = MastodonAPI.client_key,
        client_secret = MastodonAPI.client_secret,
        access_token  = MastodonAPI.access_token
    )
    api.toot(text)


def main():
    """botの実行"""
    # 日付の指定
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    now_dt = datetime.datetime.now(tz=JST)
    begin_datetime = datetime.datetime(now_dt.year, now_dt.month, now_dt.day-1, 0, 0, 0, tzinfo=JST)
    end_datetime = datetime.datetime(now_dt.year, now_dt.month, now_dt.day, 0, 0, 0, tzinfo=JST)

    # RTA動画の検索
    RTA_ids = searchRtaSnapshotApi(begin_datetime, end_datetime)
    for id in RTA_ids:
        sminfo = thumb_info.SmileVideoInfo(id)
        
        # 動画が削除されていれば飛ばす
        if not sminfo.isAlive():
            print("削除?", id)
            continue

        # 動画がタグロックされていれば、追加する
        if sminfo.isRTAtagsLock():
            print("新着!", id, sminfo.getTitle())
            try:
                tweet_RTA(sminfo)
            except:
                pass

            try:
                toot_RTA(sminfo)
            except:
                pass


def test():
    # 日付の指定
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    now_dt = datetime.datetime.now(tz=JST)
    begin_datetime = datetime.datetime(now_dt.year, now_dt.month, now_dt.day-2, 17, 0, 0, tzinfo=JST)
    end_datetime = datetime.datetime(now_dt.year, now_dt.month, now_dt.day, 0, 0, 0, tzinfo=JST)

    # RTA動画の検索
    RTA_ids = searchRtaSnapshotApi(begin_datetime, end_datetime)
    for id in RTA_ids:
        sminfo = thumb_info.SmileVideoInfo(id)

        if not sminfo.isAlive():
            print("削除?", id)
            continue

        # 動画がタグロックされていれば、追加する
        if sminfo.isRTAtagsLock():
            print("新着!", id, sminfo.getTitle())
            # tweet_RTA(sminfo)
            # toot_RTA(sminfo)

if __name__ == "__main__":
    # test()
    main()
    # print(searchRTA())
    # sminfo = thumb_info.SmileVideoInfo("sm41686885")
    # tweet_RTA(sminfo)
