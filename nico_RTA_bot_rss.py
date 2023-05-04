# 公式
import datetime
import email.utils
import tempfile
import urllib.parse

# サードパーティ
import feedparser
from mastodon import Mastodon
import tweepy
from twitter_text import parse_tweet

# 自作
import nico_getthumbinfo as thumb_info
from secret import TwitterAPI
from secret import MastodonAPI
import ogp_image

"""
# RFC2822 形式の日付
https://www.ytyng.com/blog/RFC2822%E5%BD%A2%E5%BC%8F%E3%81%AE%E6%97%A5%E4%BB%98%E3%82%92python%E3%81%AEdatetime%E3%81%AB%E5%A4%89%E6%8F%9B%E3%81%99%E3%82%8B/
"""
def parse_RFC2822_datetime(date_str_rfc2822: str):
    """RFC2822形式をパースする"""
    timetuple = email.utils.parsedate_tz(date_str_rfc2822)
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    date = datetime.datetime(*timetuple[:7], tzinfo=JST)
    return date

def test_parse_RFC2822_datetime():
    test_date_str = "Sat, 11 Feb 2023 11:44:41 +0900"
    print(test_date_str)
    print(parse_RFC2822_datetime(test_date_str))

def searchTag_RSS(tag_name, begin_datetime, end_datetime):
    # タグ検索
    rss = feedparser.parse("https://www.nicovideo.jp/tag/%s?sort=f&order=d&rss=2.0" % urllib.parse.quote(tag_name))

    content_ids = list()
    for entry in rss.entries:
        nico_url = urllib.parse.urlparse(entry.link)
        sm_id = nico_url.path.split("/")[-1]
        sm_datetime = parse_RFC2822_datetime(entry.published)

        if (begin_datetime <= sm_datetime and sm_datetime <= end_datetime):
            content_ids.append(sm_id)

    return content_ids

def searchRTA_RSS(tag_list, begin_datetime, end_datetime):
    """リアル登山アタック動画を RSS 経由で検索し、結果を返す"""
    
    content_ids = list()
    for tag_name in tag_list:
        temp_ids = searchTag_RSS(tag_name, begin_datetime, end_datetime)
        for id in temp_ids:
            if id not in content_ids:
                content_ids.append(id)

    return content_ids

def tweet_RTA(sminfo: thumb_info):
    """指定した動画をTwitterでツイートする"""
    text1 = ""
    # text1 += "テスト投稿\n"
    text1 += "《 #リアル登山アタック 新着動画》\n"
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


def toot_RTA(sminfo):
    """指定した動画をマストドンでトゥートする"""
    toot_text = ""
    # text += "開発中 テスト投稿\n"
    toot_text += "《 #リアル登山アタック 新着動画》\n"
    toot_text += sminfo.getTitle() + "\n"
    toot_text += "投稿者: %s さん\n" % sminfo.getAuthor()
    # toot_text += "タグ: %s\n" % (" ".join(sminfo.getTags()))
    toot_text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

    # 認証と投稿
    api = Mastodon(
        api_base_url  = MastodonAPI.server,
        client_id     = MastodonAPI.client_key,
        client_secret = MastodonAPI.client_secret,
        access_token  = MastodonAPI.access_token
    )
    api.toot(toot_text)


def main(tag_list):
    """botの実行"""
    # 日付の指定
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    now_dt = datetime.datetime.now(tz=JST)
    # 投稿後の待機時間
    waiting_time = datetime.timedelta(minutes=30)
    # 更新チェック間隔時間
    interval_time = datetime.timedelta(minutes=10)
    begin_datetime = now_dt - interval_time - waiting_time
    end_datetime = now_dt - waiting_time

    # RTA動画の検索
    RTA_ids = searchRTA_RSS(tag_list, begin_datetime, end_datetime)
    for id in RTA_ids:
        sminfo = thumb_info.SmileVideoInfo(id)
        
        # 動画が削除されていれば、スルー
        if not sminfo.isAlive():
            print(id, sminfo.getTitle(), "削除?")
            continue

        # 動画がタグロックされていれば、追加する
        if sminfo.isTagsLock(tag_list):
            print(id, sminfo.getTitle(), "Locked")
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

def test(tag_list):
    """botの実行"""
    # 日付の指定
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    now_dt = datetime.datetime.now(tz=JST)
    begin_datetime = datetime.datetime(2023, 4, 23,  0, 0, 0, tzinfo=JST)
    end_datetime   = datetime.datetime(2023, 4, 23, 11, 0, 0, tzinfo=JST)


    # RTA動画の検索
    RTA_ids = searchRTA_RSS(tag_list, begin_datetime, end_datetime)
    for id in RTA_ids:
        sminfo = thumb_info.SmileVideoInfo(id)
        
        # 動画が削除されていれば、スルー
        if not sminfo.isAlive():
            print(id, sminfo.getTitle(), "削除?")
            continue

        # 動画がタグロックされていれば、追加する
        if sminfo.isTagsLock(tag_list):
            print(id, sminfo.getTitle(), "Locked")
            try:
                tweet_RTA(sminfo, True)
            except:
                pass

            try:
                toot_RTA(sminfo, True)
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
    main(tag_list)

    # ツイートなし
    # test(tag_list, False)
