# 自作
import nico_RTA_bot
import nico_getthumbinfo

class ManualBot:
    def __init__(self, is_debug=True, try_tweet=False) -> None:
        self.is_debug = is_debug
        self.try_tweet = try_tweet

        print("半自動 bot", end="")
        if is_debug:
            print("【デバッグモード】ツイートなし Dry Run")
        else:
            print("【本番モード】ツイートあり")

    def tweet_RTA(self, sminfo: nico_getthumbinfo):
        """指定した動画をTwitterでツイートする"""
        text = "テスト投稿\n" if self.is_debug else ""
        text += "（半自動）《 #リアル登山アタック 新着動画》\n"
        text += "%s\n" % sminfo.getTitle()
        text += "投稿者: %s さん\n" % sminfo.getAuthor()
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        nico_RTA_bot.tweet(text, sminfo.getURL(), try_tweet=self.try_tweet)

    def toot_RTA(self, sminfo: nico_getthumbinfo):
        """指定した動画をマストドンでトゥートする"""
        text = "テスト投稿\n" if self.is_debug else ""
        text += "（半自動）《 #リアル登山アタック 動画》\n"
        text += sminfo.getTitle() + "\n"
        text += "投稿者: %s" % sminfo.getAuthor() + " さん\n"
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        nico_RTA_bot.toot(text, sminfo.getURL(), try_tweet=self.try_tweet)


if __name__ == "__main__":
    bot = ManualBot(is_debug=True, try_tweet=True)

    sm_id = "sm42356685"
    sm_info = nico_getthumbinfo.SmileVideoInfo(sm_id)
    
    bot.tweet_RTA(sm_info)
    bot.toot_RTA(sm_info)
