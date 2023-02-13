# サードパーティ
from mastodon import Mastodon
import tweepy
from twitter_text import parse_tweet

# 自作
import nico_getthumbinfo as thumb_info
from secret import TwitterAPI
from secret import MastodonAPI
from nico_RTA_bot_rss import tweet_RTA

def tweet_RTA(sminfo: thumb_info):
    """指定した動画をTwitterでツイートする"""
    text1 = ""
    # text1 += "テスト投稿\n"
    text1 += "（半手動）《 #リアル登山アタック 新着動画》\n"
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
    # text += "開発中 テスト投稿\n"
    text += "（半手動）《 #リアル登山アタック 新着動画》\n"
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


if __name__ == "__main__":
    sm_id = "sm41791472"
    sm_info = thumb_info.SmileVideoInfo(sm_id)
    tweet_RTA(sm_info)
    toot_RTA(sm_info)
