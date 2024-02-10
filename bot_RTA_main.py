# 公式
import datetime
import sys

# 自作
import nico_RTA_bot

if __name__ == "__main__":
    is_debug = not ("product" in sys.argv)
    try_post = "try_post" in sys.argv

    tag_list = [
        "RTA(リアル登山アタック)",
        "RTA(リアル登山アタック)外伝",
        "RTA(リアル登山アタック)団体戦",
        "RTA(リアル登山アタック)技術部",
    ]
    bot = nico_RTA_bot.RSSBaseBot(tag_list, "#リアル登山アタック", is_debug=is_debug, try_post=try_post)

    # 日付の指定
    JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
    now_dt = datetime.datetime.now(tz=JST)

    if bot.is_debug:
        # デバッグ時の期間指定
        begin_dt = now_dt - datetime.timedelta(days=0, hours=17)
        end_dt = now_dt

    else:    
        # 投稿後の待機時間
        waiting_time = datetime.timedelta(minutes=30)
        # 更新チェック間隔時間
        interval_time = datetime.timedelta(minutes=10)
        begin_dt = now_dt - interval_time - waiting_time
        end_dt = now_dt - waiting_time
    
    bot.main(begin_dt, end_dt)
