# 公式
import datetime
import json
import tempfile

# サードパーティ
from mastodon import Mastodon
import requests
import tweepy
from twitter_text import parse_tweet

# 自作
import nico_getthumbinfo as thumb_info
from secret import TwitterAPI
from secret import MastodonAPI
import ogp_image

def searchTagsSnapshotApi(tag_list, begin_datetime, end_datetime) -> list:
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
            "include_lower": True,  # fromを含めるならTrue
            "include_upper": False, # toを含めるならTrue
        }
    )
    # print(json_filter)

    query_tags = " OR ".join(tag_list)

    # 並び替え条件の設定
    query_param = {
        "q": query_tags,
        "targets": "tags",
        "fields": "contentId",
        "jsonFilter": json_filter,
        "_sort": "-startTime",  # 投稿が新しい順
        "_limit": 100,
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
    text1 += "%s\n" % sminfo.getTitle()
    text1 += "投稿者: %s さん\n" % sminfo.getAuthor()
    
    text3 = "#%s %s" % (sminfo.sm_id, sminfo.getURL())

    # タグの量によっては140文字制限を超えるため、調節する
    tweet_text = text1 + text3
    # tags = sminfo.getTags()
    # for i in range(1, len(tags)+1):
    #     text2 = "タグ: %s\n" % (" ".join(tags[:i]))
    #     temp = text1 + text2 + text3
    #     if parse_tweet(temp).valid:
    #         tweet_text = text1 + text2 + text3
    #     else:
    #         break

    # 認証と投稿
    auth = tweepy.OAuthHandler(TwitterAPI.consumer_key, TwitterAPI.consumer_secret)
    auth.set_access_token(TwitterAPI.access_token, TwitterAPI.access_token_secret)
    # api = tweepy.API(auth)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    
    # OGP og:image よりサムネイル画像を指定する
    fd, temp_path = tempfile.mkstemp()
    image_path = ogp_image.download_OGP_image(sminfo.getURL(), temp_path)
        
    # サムネイル画像が取得できれば画像つきツイートを行う
    if image_path is not None:
        media_ids = [api.media_upload(image_path).media_id]
        api.update_status(status=tweet_text, media_ids=media_ids)
    else:
        api.update_status(status=tweet_text)


def toot_RTA(sminfo: thumb_info):
    """指定した動画をマストドンでトゥートする"""

    text = ""
    # text += "テスト投稿\n"
    text += "《 #リアル登山アタック 昨日の新着動画》\n"
    text += "%s\n" % sminfo.getTitle()
    text += "投稿者: %s さん\n" % sminfo.getAuthor()
    # text += "タグ: %s\n" % " ".join(sminfo.getTags())
    text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

    api = Mastodon(
        api_base_url  = MastodonAPI.server,
        client_id     = MastodonAPI.client_key,
        client_secret = MastodonAPI.client_secret,
        access_token  = MastodonAPI.access_token
    )
    api.toot(text)


def main(tag_list, run=False):
    """botの実行"""
    # 日付の指定
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    now_dt = datetime.datetime.now(tz=JST)
    begin_datetime = datetime.datetime(now_dt.year, now_dt.month, now_dt.day-1, 0, 0, 0, tzinfo=JST)
    end_datetime = datetime.datetime(now_dt.year, now_dt.month, now_dt.day, 0, 0, 0, tzinfo=JST)

    # RTA動画の検索
    RTA_ids = searchTagsSnapshotApi(tag_list, begin_datetime, end_datetime)
    for id in RTA_ids:
        sminfo = thumb_info.SmileVideoInfo(id)
        
        # 動画が削除されていれば飛ばす
        if not sminfo.isAlive():
            print(id, sminfo.getTitle(), "削除?")
            continue

        # 動画がタグロックされていれば、追加する
        if sminfo.isTagsLock(tag_list):
            print(id, sminfo.getTitle(), "Locked")
            if run:
                try:
                    tweet_RTA(sminfo)
                except:
                    pass

                try:
                    toot_RTA(sminfo)
                except:
                    pass
        else:
            print(id, sminfo.getTitle(), "Unlocked")


def test(tag_list, run=False):
    """botの実行"""
    # 日付の指定
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    now_dt = datetime.datetime.now(tz=JST)
    begin_datetime = datetime.datetime(2023, 4, 21, 0, 0, 0, tzinfo=JST)
    end_datetime   = datetime.datetime(2023, 4, 22, 0, 0, 0, tzinfo=JST)

    # RTA動画の検索
    RTA_ids = searchTagsSnapshotApi(tag_list, begin_datetime, end_datetime)
    for id in RTA_ids:
        sminfo = thumb_info.SmileVideoInfo(id)
        
        # 動画が削除されていれば飛ばす
        if not sminfo.isAlive():
            print(id, sminfo.getTitle(), "削除?")
            continue

        # 動画がタグロックされていれば、追加する
        if sminfo.isTagsLock(tag_list):
            print(id, sminfo.getTitle(), "Locked")
            if run:
                try:
                    tweet_RTA(sminfo)
                except:
                    pass

                try:
                    toot_RTA(sminfo)
                except:
                    pass
        else:
            print(id, sminfo.getTitle(), "Unlocked")


if __name__ == "__main__":
    tag_list = [
        "RTA(リアル登山アタック)",
        "RTA(リアル登山アタック)外伝",
        "RTA(リアル登山アタック)団体戦",
        "RTA(リアル登山アタック)技術部",
        "1分弱登山祭2023F",
    ]

    # ツイートあり
    # main(tag_list, True)

    # ツイートなし
    test(tag_list, False)
