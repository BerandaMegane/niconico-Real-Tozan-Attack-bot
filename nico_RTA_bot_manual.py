# サードパーティ
from mastodon import Mastodon
import tweepy
from twitter_text import parse_tweet

# 自作
import nico_getthumbinfo as thumb_info
from secret import TwitterAPI
from secret import MastodonAPI
from nico_RTA_bot_rss import tweet_RTA
import ogp_image

def tweet_RTA(sminfo: thumb_info):
    """指定した動画をTwitterでツイートする"""
    text1 = ""
    # text1 += "テスト投稿\n"
    text1 += "（半手動）《 #1分弱登山祭2023F 動画》\n"
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
    
    # OGP og:image よりサムネイル画像を指定する
    image_path = ogp_image.download_OGP_image(sminfo.getURL(), "")
    
    # サムネイル画像が取得できれば画像つきツイートを行う
    if image_path is not None:
        media_ids = [api.media_upload(image_path).media_id]
        api.update_status(status=tweet_text, media_ids=media_ids)
    else:
        api.update_status(status=tweet_text)


def toot_RTA(sminfo: thumb_info):
    """指定した動画をマストドンでトゥートする"""
    text = ""
    # text += "開発中 テスト投稿\n"
    text += "（半手動）《 #1分弱登山祭2023F 動画》\n"
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


def tweet_toot_RTAs(sm_ids):
    for sm_id in sm_ids:
        sm_info = thumb_info.SmileVideoInfo(sm_id)
        print(sm_info.sm_id, "処理中")
        tweet_RTA(sm_info)
        toot_RTA(sm_info)

if __name__ == "__main__":
    # sm_id = "sm41887083"
    # sm_info = thumb_info.SmileVideoInfo(sm_id)
    # tweet_RTA(sm_info)
    # toot_RTA(sm_info)

    sm_ids = [
        "sm42076217",
        "sm42120467",
        "sm42119878",
        "sm42119846",
        "sm42116024",
        "sm42118338",
        "sm42118564",
        "sm42115563",
        "sm42118511",
        "sm42118291",
        "sm42078541",
        "sm42117216",
        "sm42075134",
        "sm42114605",
        "sm42111201",
        "sm42078576",
        "sm42068223",
        "sm42099322",
        "sm42110043",
        "sm42075038",
        "sm42109057",
        "sm42104526",
        "sm42016440",
    ]
    tweet_toot_RTAs(sm_ids)    
