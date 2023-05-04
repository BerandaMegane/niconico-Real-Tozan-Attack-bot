# 自作
import nico_RTA_bot
import nico_getthumbinfo

class ManualBot:
    def __init__(self, debug) -> None:
        self.debug = debug

    def tweet_RTA(self, sminfo: nico_getthumbinfo):
        """指定した動画をTwitterでツイートする"""
        text = "テスト投稿\n" if self.debug else ""
        text += "（半自動）《 #リアル登山アタック 新着動画》\n"
        text += "%s\n" % sminfo.getTitle()
        text += "投稿者: %s さん\n" % sminfo.getAuthor()
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        nico_RTA_bot.tweet(text, sminfo.getURL(), self.debug)

    def toot_RTA(self, sminfo: nico_getthumbinfo):
        """指定した動画をマストドンでトゥートする"""
        text = "テスト投稿\n" if self.debug else ""
        text += "（半自動）《 #リアル登山アタック 動画》\n"
        text += sminfo.getTitle() + "\n"
        text += "投稿者: %s" % sminfo.getAuthor() + " さん\n"
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        nico_RTA_bot.toot(text, sminfo.getURL(), self.debug)


if __name__ == "__main__":
    bot = ManualBot(debug=True)

    sm_id = "sm41887083"
    sm_info = nico_getthumbinfo.SmileVideoInfo(sm_id)
    
    bot.tweet_RTA(sm_info)
    bot.toot_RTA(sm_info)
