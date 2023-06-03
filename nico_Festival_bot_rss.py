# 公式
import datetime
import email.utils
import urllib.parse

# サードパーティ
import feedparser

# 自作
import nico_getthumbinfo
import nico_RTA_bot
import secret

"""
# RFC2822 形式の日付
https://www.ytyng.com/blog/RFC2822%E5%BD%A2%E5%BC%8F%E3%81%AE%E6%97%A5%E4%BB%98%E3%82%92python%E3%81%AEdatetime%E3%81%AB%E5%A4%89%E6%8F%9B%E3%81%99%E3%82%8B/
"""

class RSSBaseBot:
    def __init__(self, debug, tag_list) -> None:
        self.debug = debug
        self.tag_list = tag_list
        
        if debug:
            print("【デバッグモード】")
        else:
            print("【本番モード】")

    def parse_RFC2822_datetime(self, date_str_rfc2822: str):
        """RFC2822形式をパースする"""
        timetuple = email.utils.parsedate_tz(date_str_rfc2822)
        JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
        date = datetime.datetime(*timetuple[:7], tzinfo=JST)
        return date

    def searchTag_RSS(self, tag_name, begin_dt, end_dt):
        # タグ検索
        rss = feedparser.parse("https://www.nicovideo.jp/tag/%s?sort=f&order=d&rss=2.0" % urllib.parse.quote(tag_name))

        content_ids = list()
        for entry in rss.entries:
            nico_url = urllib.parse.urlparse(entry.link)
            sm_id = nico_url.path.split("/")[-1]
            sm_dt = self.parse_RFC2822_datetime(entry.published)

            if (begin_dt <= sm_dt and sm_dt <= end_dt):
                content_ids.append(sm_id)

        return content_ids

    def searchRTA_RSS(self, begin_dt, end_dt):
        """動画を RSS 経由で検索し、結果を返す"""
        
        content_ids = list()
        for tag_name in self.tag_list:
            temp_ids = self.searchTag_RSS(tag_name, begin_dt, end_dt)
            for id in temp_ids:
                if id not in content_ids:
                    content_ids.append(id)

        return content_ids

    def tweet_RTA(self, sminfo: nico_getthumbinfo):
        """指定した動画をTwitterでツイートする"""
        text = "テスト投稿\n" if self.debug else ""
        text += "《 #ニコニコ星まつり・天体観測 新着動画》\n"
        text += "%s\n" % sminfo.getTitle()
        text += "投稿者: %s さん\n" % sminfo.getAuthor()
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        nico_RTA_bot.tweet(text, sminfo.getURL(), self.debug)

    def toot_RTA(self, sminfo: nico_getthumbinfo):
        """指定した動画をマストドンでトゥートする"""
        text = "テスト投稿\n" if self.debug else ""
        text += "《 #ニコニコ星まつり・天体観測 動画》\n"
        text += sminfo.getTitle() + "\n"
        text += "投稿者: %s" % sminfo.getAuthor() + " さん\n"
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        nico_RTA_bot.toot(text, sminfo.getURL(), self.debug)

    def main(self, begin_dt, end_dt):
        # RTA動画の検索
        RTA_ids = self.searchRTA_RSS(begin_dt, end_dt)
        for id in RTA_ids:
            sminfo = nico_getthumbinfo.SmileVideoInfo(id)
            
            # 動画が削除されていれば、スルー
            if not sminfo.isAlive():
                print(id, sminfo.getTitle(), "削除?")
                continue

            # 動画がタグロックされていれば、追加する
            if sminfo.isTagsLock(self.tag_list):
                print(id, sminfo.getTitle(), "Locked")
                try:
                    self.tweet_RTA(sminfo)
                except:
                    pass

                try:
                    self.toot_RTA(sminfo)
                except:
                    pass
            else:
                print(id, sminfo.getTitle(), "Unlocked")


def test_parse_RFC2822_datetime():
    test_date_str = "Sat, 11 Feb 2023 11:44:41 +0900"
    print(test_date_str)

    bot = RSSBaseBot(secret.Environment.debug, tag_list)
    print(bot.parse_RFC2822_datetime(test_date_str))

if __name__ == "__main__":

    tag_list = [
        "ニコニコ星まつり",
        "天体観測",
    ]
    bot = RSSBaseBot(secret.Environment.debug, tag_list)

    # 日付の指定
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    now_dt = datetime.datetime.now(tz=JST)

    if secret.Environment.debug:
        # デバッグ時の期間指定
        begin_dt = now_dt - datetime.timedelta(hours=72)
        end_dt = now_dt

    else:    
        # 投稿後の待機時間
        waiting_time = datetime.timedelta(minutes=30)
        # 更新チェック間隔時間
        interval_time = datetime.timedelta(minutes=10)
        begin_dt = now_dt - interval_time - waiting_time
        end_dt = now_dt - waiting_time
    
    bot.main(begin_dt, end_dt)
