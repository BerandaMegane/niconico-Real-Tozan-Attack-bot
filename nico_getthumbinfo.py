# 公式
import datetime
import xml.etree.ElementTree as ET

# サードパーティ
import requests
import mojimoji

"""
# 参考URL
* Qiita - python:requestsでニコニコ動画APIを使う
https://qiita.com/be_tiger/items/a086380121a5cefe6eef

* ニコニコ大百科 - ニコニコ動画API（APIリファレンス）
https://dic.nicovideo.jp/a/%E3%83%8B%E3%82%B3%E3%83%8B%E3%82%B3%E5%8B%95%E7%94%BBapi
"""

class SmileVideoInfo:
    """
    動画情報取得クラス
    """
    def __init__(self, sm_id:str) -> None:
        self.fetchVideoInfo(sm_id)

    def fetchVideoInfo(self, sm_id:str) -> None:
        """
        ニコニコ動画IDを設定し、情報を取得する
        """
        self.sm_id = sm_id

        # API エンドポイント
        url = "https://ext.nicovideo.jp/api/getthumbinfo/" + self.sm_id

        # カスタムヘッダ
        headers = {"User-Agent": "RealTozanAttack-TwitterBot"}

        # API
        res = requests.get(url, headers=headers)
        self.root = ET.fromstring(res.text)
        # print(self.root)
    
    @classmethod
    def normalize_name(cls, name:str):
        # 文字列を半角・大文字に正規化する
        return str.upper(mojimoji.zen_to_han(name))

    @classmethod
    def isEqualTagName(cls, tag1:str, tag2:str):
        # 文字列を正規化して比較する
        return cls.normalize_name(tag1) == cls.normalize_name(tag2)

    def isAlive(self) -> bool:
        # 動画が制限されていなければ True
        return self.root.attrib["status"] == "ok"
    
    def isTagLock(self, tag:str) -> bool:
        # 指定されたタグがロックされていれば True
        return "lock" in tag.attrib and tag.attrib["lock"] == "1"
        
    def isTagsLock(self, tag_list) -> bool:
        # リアル登山アタック関連タグがロックされていれば True
        tags = self.root.find("thumb").find("tags")
        # print(tags)
        for tag in tags:
            # print(tag.text, tag.attrib)
            for name in tag_list:
                if self.isEqualTagName(tag.text, name) and self.isTagLock(tag):
                    return True
        else:
            return False
    
    def getThumbInfo(self):
        return self.root.find("thumb")

    def getThumbInfoAtrrib(self, attrib:str):
        return self.getThumbInfo().find(attrib).text

    def getTitle(self) -> str:
        # 動画タイトル
        return self.getThumbInfoAtrrib("title")

    def getDatetime(self) -> datetime.datetime:
        # 投稿時間
        text = self.getThumbInfoAtrrib("first_retrieve")
        return datetime.datetime.fromisoformat(text)
    
    def getAuthor(self) -> str:
        # 投稿者名
        return self.getThumbInfoAtrrib("user_nickname")
    
    def getAuthorId(self) -> str:
        # 投稿者ID
        return self.getThumbInfoAtrrib("user_id")
    
    def getURL(self) -> str:
        # 動画URL
        return self.getThumbInfoAtrrib("watch_url")

    def getTags(self) -> list:
        # 動画につけられたタグリスト
        tags = self.root.find("thumb").find("tags")
        return [tag.text for tag in tags]

if __name__ == "__main__":
    test_sm = SmileVideoInfo("sm41686885")
    
    tag_list = [
        "RTA(リアル登山アタック)",
        "RTA(リアル登山アタック)外伝",
        "RTA(リアル登山アタック)団体戦",
        "RTA(リアル登山アタック)技術部",
        "1分弱登山祭2023F",
    ]

    print(test_sm.getThumbInfo())
    print(test_sm.isTagsLock(tag_list))
    print(test_sm.isAlive())
    print(test_sm.getTitle())
    print(test_sm.getDatetime())
    print(test_sm.getAuthor())
    print(test_sm.getURL())
    print(test_sm.getTags())
