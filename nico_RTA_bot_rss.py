# 公式
import datetime
import email.utils

# サードパーティ
import feedparser
from mastodon import Mastodon
import tweepy
from urllib.parse import urlparse

# 自作
import nico_getthumbinfo as thumb_info
from secret import TwitterAPI
from secret import MastodonAPI


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


def searchRTA_RSS(begin_datetime, end_datetime):
    """リアル登山アタック動画を RSS 経由で検索し、結果を返す"""
    
    # タグ検索「RTA（リアル登山アタック）」
    rss = feedparser.parse("https://www.nicovideo.jp/tag/RTA%EF%BC%88%E3%83%AA%E3%82%A2%E3%83%AB%E7%99%BB%E5%B1%B1%E3%82%A2%E3%82%BF%E3%83%83%E3%82%AF%EF%BC%89?sort=f&order=d&rss=2.0")

    contents_ids = list()
    for entry in rss.entries:
        nico_url = urlparse(entry.link)
        sm_id = nico_url.path.split("/")[-1]
        sm_datetime = parse_RFC2822_datetime(entry.published)

        if (begin_datetime <= sm_datetime and sm_datetime <= end_datetime):
            # print("新着!", sm_id, sm_datetime)
            contents_ids.append(sm_id)
        else:
            break
    
    return contents_ids


def tweet_RTA(sminfo: thumb_info):
    """指定した動画をTwitterでツイートする"""
    text1 = ""
    # text1 += "テスト投稿\n"
    text1 += "《 #リアル登山アタック 新着動画》\n"
    text1 += sminfo.getTitle() + "\n"
    text1 += "投稿者: %s" % sminfo.getAuthor() + " さん\n"
    
    text3 = ""
    text3 += "#%s" % sminfo.sm_id + "\n"
    text3 += sminfo.getURL()

    # タグの量によっては280文字制限を超えるため、調節する
    text2 = "タグ:"
    for tag in sminfo.getTags():
        text_l = len(text1) + len(text2) + len(text3)
        tag_l = len(tag)
        if (text_l + tag_l + 1) < 280:
            text2 += " " + tag
        else:
            text2 += "\n"
            break
    else:
        text2 += "\n"
    
    text = text1 + text2 + text3
    print(text)

    # 認証と投稿
    auth = tweepy.OAuthHandler(TwitterAPI.consumer_key, TwitterAPI.consumer_secret)
    auth.set_access_token(TwitterAPI.access_token, TwitterAPI.access_token_secret)
    # api = tweepy.API(auth)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    api.update_status(status=text)


def toot_RTA(sminfo):
    """指定した動画をマストドンでトゥートする"""
    text = ""
    # text += "開発中 テスト投稿\n"
    text += "《 #リアル登山アタック 新着動画》\n"
    text += sminfo.getTitle() + "\n"
    text += "投稿者: %s" % sminfo.getAuthor() + " さん\n"
    text += "タグ: " + (" ".join(sminfo.getTags())) + "\n"
    text += "#%s" % sminfo.sm_id + "\n"
    text += sminfo.getURL()

    # 認証と投稿
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
    begin_datetime = now_dt - datetime.timedelta(hours=1)
    end_datetime = now_dt

    # RTA動画の検索
    RTA_ids = searchRTA_RSS(begin_datetime, end_datetime)
    for id in RTA_ids:
        sminfo = thumb_info.SmileVideoInfo(id)
        
        # 動画が削除されていれば、スルー
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
    begin_datetime = now_dt - datetime.timedelta(hours=12)
    end_datetime = now_dt

    # RTA動画の検索
    RTA_ids = searchRTA_RSS(begin_datetime, end_datetime)
    for id in RTA_ids:
        sminfo = thumb_info.SmileVideoInfo(id)

        if not sminfo.isAlive():
            print("削除?", id)
            continue

        # 動画がタグロックされていれば、追加する
        if sminfo.isRTAtagsLock():
            print("新着!", id, sminfo.getTitle())
            # tweet_RTA(sminfo)

if __name__ == "__main__":
    main()
    # test()

    # テスト date parser
    # test_parse_RFC2822_datetime()
