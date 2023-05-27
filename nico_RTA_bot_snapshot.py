# 公式
import datetime
import json

# サードパーティ
import requests

# 自作
import nico_getthumbinfo
import nico_RTA_bot
import secret

"""
参考: Qiita - python:requestsでニコニコ動画APIを使う
https://qiita.com/be_tiger/items/a086380121a5cefe6eef
"""

class SnapshotBaseBot:
    def __init__(self, debug, tag_list) -> None:
        self.debug = debug
        self.tag_list = tag_list
        
        if debug:
            print("【デバッグモード】")
        else:
            print("【本番モード】")

    def searchTagsSnapshotApi(self, begin_datetime, end_datetime) -> list:
        """リアル登山アタック動画を Snapshot API 経由で検索し、結果を返す"""

        # APIのエンドポイント
        url = "https://api.search.nicovideo.jp/api/v2/snapshot/video/contents/search"

        # 抽出条件の指定
        json_filter = json.dumps(
            {
                "type": "range",
                "field": "startTime",
                "from": begin_datetime.isoformat(timespec="seconds"),
                "to": end_datetime.isoformat(timespec="seconds"),
                "include_lower": True,  # fromを含めるならTrue
                "include_upper": False, # toを含めるならTrue
            }
        )

        query_tags = " OR ".join(tag_list)

        # 並び替え条件の設定
        query_param = {
            "q": query_tags,
            "targets": "tags",
            "fields": "contentId",
            "jsonFilter": json_filter,
            "_sort": "-startTime",  # 投稿が新しい順
            "_limit": 100,
        }

        # カスタムヘッダの指定（指定が推奨されているらしい）
        headers = {"User-Agent": "RealTozanAttack-TwitterBot"}

        # API の実行
        res = requests.get(url, params=query_param, headers=headers)

        # 正常に取得できなかった場合は空のリストを返す
        if res.status_code != requests.codes.ok or res.json()["meta"]["status"] != 200:
            return []

        # 正常取得時の応答文字列
        """
        {'data': [{'contentId': 'sm41705968'},
                {'contentId': 'sm41701466'},
                {'contentId': 'sm41700684'},
                {'contentId': 'sm41686885'},
                {'contentId': 'sm41687602'},
                {'contentId': 'sm41687114'},
                {'contentId': 'sm41686241'},
                {'contentId': 'sm41678864'},
                {'contentId': 'sm41678019'},
                {'contentId': 'sm41676393'}],
        'meta': {'id': '5ece8017-1c75-4c0c-8414-564175237077',
                'status': 200,
                'totalCount': 3005}}
        """

        contents_ids = [str(x["contentId"]) for x in res.json()["data"]]
        return contents_ids

    def tweet_RTA(self, sminfo: nico_getthumbinfo):
        """指定した動画をTwitterでツイートする"""
        text = "テスト投稿\n" if self.debug else ""
        text += "《 #リアル登山アタック 新着動画》\n"
        text += "%s\n" % sminfo.getTitle()
        text += "投稿者: %s さん\n" % sminfo.getAuthor()
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        nico_RTA_bot.tweet(text, sminfo.getURL(), self.debug)

    def toot_RTA(self, sminfo: nico_getthumbinfo):
        """指定した動画をマストドンでトゥートする"""
        text = "テスト投稿\n" if self.debug else ""
        text += "《 #リアル登山アタック 動画》\n"
        text += sminfo.getTitle() + "\n"
        text += "投稿者: %s" % sminfo.getAuthor() + " さん\n"
        text += "#%s %s" % (sminfo.sm_id, sminfo.getURL())

        nico_RTA_bot.toot(text, sminfo.getURL(), self.debug)

    def main(self, begin_dt, end_dt):
        """botの実行"""
        
        # RTA動画の検索
        RTA_ids = self.searchTagsSnapshotApi(begin_dt, end_dt)
        for id in RTA_ids:
            sminfo = nico_getthumbinfo.SmileVideoInfo(id)
            
            # 動画が削除されていれば飛ばす
            if not sminfo.isAlive():
                print(id, sminfo.getTitle(), "削除?")
                continue

            # 動画がタグロックされていれば、追加する
            if sminfo.isTagsLock(tag_list):
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


if __name__ == "__main__":

    tag_list = [
        "RTA(リアル登山アタック)",
        "RTA(リアル登山アタック)外伝",
        "RTA(リアル登山アタック)団体戦",
        "RTA(リアル登山アタック)技術部",
    ]
    bot = SnapshotBaseBot(secret.Environment.debug, tag_list)

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
