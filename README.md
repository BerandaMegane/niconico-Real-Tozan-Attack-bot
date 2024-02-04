# niconico Real-Tozan-Attack bot
ニコニコ動画に投稿されている「リアル登山アタック」の新着動画を自動ツイートするPythonスクリプト

[リアル登山アタックとは（ニコニコ大百科）](https://dic.nicovideo.jp/a/rta%28%E3%83%AA%E3%82%A2%E3%83%AB%E7%99%BB%E5%B1%B1%E3%82%A2%E3%82%BF%E3%83%83%E3%82%AF%29)

## 運用について
### リアル登山アタック新着bot @RTA_BaseCamp
* https://twitter.com/RTA_BaseCamp
* https://mastodon-japan.net/@RTA_BaseCamp

## 使用方法 (Linux)
環境構築から使用するまでを紹介します。
1. リポジトリを自分のPCやサーバにコピーします
```bash
git clone https://github.com/BerandaMegane/niconico-Real-Tozan-Attack-bot.git
```

2. venv 仮想環境の構築・アクティベート
```bash
python -m venv venv
source ./venv/bin/activate
```

2. 必要なPythonおよびライブラリをインストールします
```bash
# requirements.txt でインストール
pip install -r requirements.txt
# pip install で直接インストール
pip install bs4 feedparser Mastodon.py mojimoji requests tweepy twitter-text-parser urllib3 pip-review
```

3. `secret-sample.py` を `secret.py` に名前を変更します
```bash
mv secret-sample.py secret.py
```

4. `secret.py` の中に Twitter および Mastodon で自動ツイートするための API キーを入力します
```bash
vi secret.py
```

5. `nico_RTA_bot_rss.py` または `nico_RTA_bot_snapshot.py` を定期実行します
```bash
sudo vi /etc/crontab
```
```
# 1日ごとに実行
0 20 *  *  *  ubuntu /usr/bin/python3 /[path]/nico_RTA_bot_snapshot.py
# 10分ごとに実行
*/10 *  *  *  *  ubuntu /usr/bin/python3 /[path]/nico_RTA_bot_rss.py
```

なお、`nico_RTA_bot_rss.py` は10分ごと、`nico_RTA_bot_snapshot.py`は1日ごとに実行することを想定しています。

## 動作に必要なライブラリ等
requirements.txt を参照してください。

## 連絡先
* めがね
  * https://twitter.com/BerandaMegane
  * https://mastodon-japan.net/@VerandaMegane

## 謝辞
Twitterアカウント「RTAの山小屋 [@RTA_Lodge](https://twitter.com/RTA_Lodge)」を運営されている [@NermanZou](https://twitter.com/NermanZou) さん、大変参考になりました。ありがとうございます。  
普段、リアル登山アタック動画を作られている走者の方々、ありがとうございます。  
もっと走って？私もたまに走ってるんだからさ。

## ライセンス
NYSL - 煮るなり焼くなり好きにしろライセンス
* http://www.kmonos.net/nysl/
* http://www.kmonos.net/nysl/index.en.html
