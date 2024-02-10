# 公式
import datetime
import sys

# 自作
import nico_RTA_bot

if __name__ == "__main__":
    is_debug = not ("product" in sys.argv)
    try_post = "try_post" in sys.argv

    tag_list = [
        "ニコニコ登山祭",
        "ニコニコ登山祭前夜祭",
        "ニコニコ登山祭後夜祭",
        "ニコニコ登山祭：１分弱",
        "ニコニコ登山祭：リアル登山アタック",
        "ニコニコ登山祭：蔵出し",
        "ニコニコ登山祭：ノンキャラクター",
    ]
    bot = nico_RTA_bot.RSSBaseBot(tag_list, "#ニコニコ登山祭", is_debug=is_debug, try_post=try_post)

    # 日付の指定
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    now_dt = datetime.datetime.now(tz=JST)

    if bot.is_debug:
        # デバッグ時の期間指定
        begin_dt = now_dt - datetime.timedelta(days=5)
        end_dt = now_dt

    else:    
        # 投稿後の待機時間
        waiting_time = datetime.timedelta(minutes=30)
        # 更新チェック間隔時間
        interval_time = datetime.timedelta(minutes=10)
        begin_dt = now_dt - interval_time - waiting_time
        end_dt = now_dt - waiting_time
    
    bot.main(begin_dt, end_dt)
