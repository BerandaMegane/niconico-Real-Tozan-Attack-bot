# 公式
import datetime
import email.utils
import tempfile
import traceback
import urllib.parse

# サードパーティ
import atproto
import feedparser
import mastodon
import tweepy

# 自作
import nico_getthumbinfo
import ogp_image
import secret

def get_TwitterAPI_handler(config):
    # Twitter API 認証
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)
    api = tweepy.API(auth)
    client = tweepy.Client(
        consumer_key=config.consumer_key,
        consumer_secret=config.consumer_secret,
        access_token=config.access_token,
        access_token_secret=config.access_token_secret
    )
    return api, client

def get_MastodonAPI_handler(config):
    # Mastodon API 認証
    return mastodon.Mastodon(
        api_base_url  = config.server,
        client_id     = config.client_key,
        client_secret = config.client_secret,
        access_token  = config.access_token
    )

def get_BlueskyAPI_handler(config):
    # Bluesky メールアドレス認証
    client = atproto.Client()
    client.login(config.email, config.password)
    return client

def post_twitter(post_text, image_url, try_post=False):
    # ログ用
    print("【Twitter】")
    print(post_text)
    
    if try_post:
        api, client = get_TwitterAPI_handler(secret.TwitterAPI)
        
        with tempfile.NamedTemporaryFile() as fp:
            # 一時ファイルにサムネイル画像ダウンロード
            image_path = ogp_image.download_OGP_image(image_url, fp)
            
            if image_path is not None:
                media_ids = [api.media_upload(image_path, file=fp).media_id]
                client.create_tweet(text=post_text, media_ids=media_ids)
            else:
                client.create_tweet(text=post_text)

def post_mastodon(post_text, image_url, try_post=False):
    # ログ用
    print("【Mastodon】")
    print(post_text)

    if try_post:
        api = get_MastodonAPI_handler(secret.MastodonAPI)
        api.toot(post_text)

def post_bluesky(post_text, image_url, image_alt, try_post=False):
    # ログ用
    print("【Bluesky】")
    print(post_text)

    if try_post:
        client = get_BlueskyAPI_handler(secret.BlueskyAPI)

        with tempfile.NamedTemporaryFile() as fp:
            # 一時ファイルにサムネイル画像をダウンロード
            image_path = ogp_image.download_OGP_image(image_url, fp)
            if image_path is not None:
                client.send_image(post_text, fp, image_alt)
            else:
                client.send_post(post_text)

def parse_RFC2822_datetime(date_str_rfc2822: str):
    """RFC2822形式をパースする"""

    """
    # 参考
    ## RFC2822 形式の日付
    https://www.ytyng.com/blog/RFC2822%E5%BD%A2%E5%BC%8F%E3%81%AE%E6%97%A5%E4%BB%98%E3%82%92python%E3%81%AEdatetime%E3%81%AB%E5%A4%89%E6%8F%9B%E3%81%99%E3%82%8B/
    """
    timetuple = email.utils.parsedate_tz(date_str_rfc2822)
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    date = datetime.datetime(*timetuple[:7], tzinfo=JST)
    return date

def test_parse_RFC2822_datetime():
    test_date_str = "Sat, 11 Feb 2023 11:44:41 +0900"
    print(test_date_str)
    print(parse_RFC2822_datetime(test_date_str))

class RSSBaseBot:
    def __init__(self, tag_list, hashtag, is_debug=True, try_post=False) -> None:
        self.tag_list = tag_list
        self.hashtag = hashtag
        self.is_debug = is_debug
        self.try_post = try_post
        
        print("RSS bot", end="")
        if self.is_debug:
            print("【デバッグモード】", end="")
        else:
            print("【本番モード】", end="")
        
        if self.try_post:
            print("ツイートあり")
        else:
            print("ツイートなし")

    def searchTag_RSS(self, tag_name, begin_dt, end_dt):
        # タグ検索
        rss = feedparser.parse("https://www.nicovideo.jp/tag/%s?sort=f&order=d&rss=2.0" % urllib.parse.quote(tag_name))

        content_ids = list()
        for entry in rss.entries:
            nico_url = urllib.parse.urlparse(entry.link)
            sm_id = nico_url.path.split("/")[-1]
            sm_dt = parse_RFC2822_datetime(entry.published)

            if (begin_dt <= sm_dt and sm_dt <= end_dt):
                content_ids.append(sm_id)

        return content_ids

    def searchRTA_RSS(self, begin_dt, end_dt):
        """リアル登山アタック動画を RSS 経由で検索し、結果を返す"""
        
        content_ids = list()
        for tag_name in self.tag_list:
            temp_ids = self.searchTag_RSS(tag_name, begin_dt, end_dt)
            for id in temp_ids:
                if id not in content_ids:
                    content_ids.append(id)

        return content_ids

    def post_twitter_RTA(self, sminfo: nico_getthumbinfo):
        
        """指定した動画をTwitterでツイートする"""
        text = "（デバッグ中）\n" if self.is_debug else ""
        text += "《 %s 新着 》\n" % self.hashtag
        text += "%s\n" % sminfo.getTitle()
        text += "投稿者: %s さん\n" % sminfo.getAuthor()
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        post_twitter(text, sminfo.getURL(), self.try_post)

    def post_mastodon_RTA(self, sminfo: nico_getthumbinfo):
        """指定した動画をマストドンでトゥートする"""
        text = "（デバッグ中）\n" if self.is_debug else ""
        text += "《 %s 新着 》\n" % self.hashtag
        text += sminfo.getTitle() + "\n"
        text += "投稿者: %s" % sminfo.getAuthor() + " さん\n"
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        post_mastodon(text, sminfo.getURL(), self.try_post)

    def post_bluesky_RTA(self, sminfo: nico_getthumbinfo):
        """指定した動画を Bluesky にポストする"""
        text = "（デバッグ中）\n" if self.is_debug else ""
        text += "《 %s 新着 》\n" % self.hashtag
        text += "%s\n" % sminfo.getTitle()
        text += "投稿者: %s さん\n" % sminfo.getAuthor()
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        image_alt = "投稿者: %s さん\n" % sminfo.getAuthor()
        image_alt += "%s\n" % sminfo.getTitle()
        image_alt += "%s" % sminfo.getURL()

        post_bluesky(text, sminfo.getURL(), image_alt, self.try_post)

    def main(self, begin_dt, end_dt):
        # RTA動画の検索
        RTA_ids = self.searchRTA_RSS(begin_dt, end_dt)

        for id in RTA_ids:
            sminfo = nico_getthumbinfo.SmileVideoInfo(id)
            
            # 動画が削除されていれば、スルー
            if not sminfo.isAlive():
                print("ヒット（削除済み）", id, sminfo.getTitle())
                continue

            # 動画がタグロックされていれば、追加する
            if sminfo.isTagsLock(self.tag_list):
                print("ヒット（タグロック済み）", id, sminfo.getTitle())
                try:
                    self.post_twitter_RTA(sminfo)
                except:
                    traceback.print_exc()

                try:
                    self.post_mastodon_RTA(sminfo)
                except:
                    traceback.print_exc()

                try:
                    self.post_bluesky_RTA(sminfo)
                except:
                    traceback.print_exc()
            else:
                print("ヒット（タグロックなし）", id, sminfo.getTitle())
